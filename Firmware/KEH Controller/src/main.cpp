#define CIRCULAR_BUFFER_INT_SAFE

#include <Arduino.h>
#include <util/atomic.h>
#include <CircularBuffer.hpp>

// ============================================================================
// Keyboard Matrix Mapping 
// ============================================================================
// Rows: PA0-PA7 (VIA Port A)
// Columns: PB0-PB7 (VIA Port B)
//
//      PB0    PB1    PB2    PB3    PB4    PB5    PB6    PB7
// PA0:  `      1      2      3      4      5      6      7
// PA1:  8      9      0      -      =      BS     ESC    TAB
// PA2:  q      w      e      r      t      y      u      i
// PA3:  o      p      [      ]      \      INS    CAPS   a
// PA4:  s      d      f      g      h      j      k      l
// PA5:  ;      '      ENTER  DEL    SHIFT  z      x      c
// PA6:  v      b      n      m      ,      .      /      UP
// PA7:  CTRL   GUI    ALT    SPACE  FN     LEFT   DOWN   RIGHT
//
// Notes:
// - BS = Backspace (0x08), ESC = Escape (0x1B), TAB (0x09)
// - INS = Insert (0x1A), DEL = Delete (0x7F), ENTER (0x0D)
// - Arrow keys: UP (0x1E), LEFT (0x1C), DOWN (0x1F), RIGHT (0x1D)
// - Function keys F1-F10 are mapped as FN + number keys 1-0
// ============================================================================

// ATmega1284 PORT A / 6522 VIA PORT A
#define VIA_PA0 24
#define VIA_PA1 25
#define VIA_PA2 26
#define VIA_PA3 27
#define VIA_PA4 28
#define VIA_PA5 29
#define VIA_PA6 30
#define VIA_PA7 31

// ATmega1284 PORT B / 6522 VIA PORT B
#define VIA_PB0 0
#define VIA_PB1 1
#define VIA_PB2 2
#define VIA_PB3 3
#define VIA_PB4 4
#define VIA_PB5 5
#define VIA_PB6 6
#define VIA_PB7 7

#define VIA_CA1 8
#define VIA_CA2 9
#define PS2CLK  10
#define PS2DATA 11

// PS2CLK (D10) is PD2, read straight from the register in the clock
// interrupt. If PS2CLK ever moves, this must move with it.
#define PS2CLK_IS_HIGH() (PIND & _BV(PD2))
#define VIA_CB1 12
#define VIA_CB2 13

#define BUFFER_SIZE 16

CircularBuffer<uint8_t, BUFFER_SIZE> ps2Buffer;  // Buffer for PS/2 keyboard data
CircularBuffer<uint8_t, BUFFER_SIZE> matrixBuffer;  // Buffer for matrix keyboard data

// PS/2 keyboard state
bool ps2Enabled = false;
bool shiftPressed = false;
bool ctrlPressed = false;
bool breakCodeNext = false;
bool extendedCodeNext = false;

// Matrix keyboard state
bool matrixEnabled = false;
bool matrixShiftPressed = false;
bool matrixCtrlPressed = false;

// Matrix key debouncing
uint8_t matrixKeyState[8][8] = {0};  // Current state of each key
uint8_t matrixKeyLast[8][8] = {0};   // Last state of each key
unsigned long matrixLastScan = 0;
uint8_t matrixScanRow = 0;   // Next row to scan; an interrupted sweep resumes here
#define MATRIX_SCAN_INTERVAL 10  // Scan every 10ms
#define MATRIX_DEBOUNCE_COUNT 2  // Key must be stable for 2 scans

// ============================================================================
// Joystick State
// ============================================================================
// The two sticks share the sixteen VIA port lines with the key matrix:
// JOYSTICK A on PA0-PA7 (the matrix rows) and JOYSTICK B on PB0-PB7 (the
// columns). Every signal is active low -- the switches close to ground -- so an
// untouched stick leaves its lines pulled high.
//
// Nothing about the sticks is sent to the 6502 from here. The 6502 reads them
// itself: Kernal KBDisable takes both encoders offline, this ATmega lets go of
// the ports, and the 6502 reads the raw ports with the sticks the only things
// pulling on them. That is the same arrangement a C64 has, it needs no wire
// protocol, and it is the only way both sticks can be read reliably.
//
// The switches sit on the very lines the key codes go out on, with nothing in
// series, so this encoder never drives a port line high: a held stick would
// short it to ground. Key codes go out open-drain instead -- see VIA Port Access.
//
// What the firmware does need is to know which lines a stick is holding down.
// A held signal pins its line low for as long as it is held, and every key
// along that row or column then reads as pressed. The matrix sweep looks for
// the sticks itself, just before each row (see scanMatrix()). These masks,
// taken once a sweep, are what sendCode() checks a failed read-back against.
uint8_t joyRowMask = 0;   // PA lines JOYSTICK A is holding low
uint8_t joyColMask = 0;   // PB lines JOYSTICK B is holding low

void onInterrupt();
void enablePS2();
void disablePS2();
void enableMatrix();
void disableMatrix();
void ps2ToAscii(uint8_t scancode);
bool scanMatrix();
uint8_t mapMatrixToAscii(uint8_t row, uint8_t col);
void serviceEncoderEnables();
void serviceHold();
void endHold();
void sampleJoystickMasks();

// ============================================================================
// VIA Port Access
// ============================================================================
// On the MightyCore "standard" pinout VIA_PA0-PA7 are D24-D31, which is exactly
// ATmega PORTA bits 0-7, and VIA_PB0-PB7 are D0-D7, which is exactly PORTB bits
// 0-7. Nothing else on this board lives on either register, so the whole port
// can be manipulated in a single instruction.
//
// That matters in three places. The encoder must let go of a port within 100 us
// of being asked, because that is how the 6502 reads the joysticks at all and
// Kernal KBDisable waits about that long before reading. So the release path
// has to be effectively instantaneous, and the scan loop has to be able to
// check for a release request without paying ~4 us per Arduino call. And the
// read-back before a strobe (below) has to be a fraction of a microsecond from
// the strobe itself. Everything that is not on those paths keeps using
// pinMode/digitalRead.
//
// If the VIA_Px pin defines above ever change, these must change with them.
//
// Nothing on either port is ever driven high. The joystick switches ground
// these same lines with nothing in series, so a line driven high under a held
// stick is an ATmega output shorted to ground. Every line idles as an input
// with its pull-up on. A key code goes out open-drain: its 0 bits are driven
// low and its 1 bits are left to the pull-ups -- the ACE Board's 1k, or on a
// COB or VCS the helper board's, with the ATmega's own ~20-50k always on too.
//
// That makes a held stick visible: a 1 bit it is holding low reads back as 0.
// So the code is read back before the strobe, and if it does not match, nothing
// is strobed and the key stays queued until the stick lets go. A key arrives
// late, never wrong. Two keys held in one row bridge columns through their
// switches and read back wrong the same way, so that needs no case of its own.
//
// After its strobe, a code stays on the port for CODE_HOLD_US, so a program
// that polls the VIA's flag once a frame rather than taking the interrupt still
// reads the code and not an idle port (the VIA is not set to latch its input).
// Only one port holds a code at a time, and the matrix sweep waits for it: the
// ports are wired to each other through the key switches, so anything driven
// on one can show up on the other.

// CA2 (PD1) and CB2 (PD5) are the 6502 asking for a port back, active high.
#define CA2_RELEASE_REQUESTED() (PIND & _BV(PD1))
#define CB2_RELEASE_REQUESTED() (PIND & _BV(PD5))

// CA1 (PD0) and CB1 (PD4) are the strobes. The VIA raises the flag on the
// falling edge (Kernal InitKB sets both to negative edge).
#define CA1_STROBE _BV(PD0)
#define CB1_STROBE _BV(PD4)

// How long a line left to its pull-up is given to rise before it is read. Sized
// for the weak case -- a port with no external pull-up, charging the bus and a
// joystick cable through the ATmega's own ~30k -- and it is a physical wait,
// not an instruction count.
#define LINE_RISE_US 10

// How long a code stays on the port after its strobe. The Kernal's interrupt
// handler reads it within ~90 us, but a program that polls the VIA's flag once a
// frame (Wizards Lab does) reads it up to a frame later. 20 ms covers a frame at
// 50 or 60 Hz, and still lets fifty keys a second through.
#define CODE_HOLD_US 20000UL

// A key the sticks are holding back is tried again this often, rather than on
// every pass of loop(), so the port is not flickering between code and idle.
#define RETRY_INTERVAL_US 1000UL

// How long after letting go of a line it was driving low the firmware waits
// before it starts a matrix sweep. A released line rises on its pull-up alone,
// and one with a long cable on it (a joystick's) can take longer than a
// sweep's 10 us settle; read too soon, it is a key that nobody pressed. At the
// bench a code's release followed straight by a sweep typed phantom 1s, row
// 0 being read first and column 1 rising slowest.
#define RELEASE_SETTLE_US 500UL

// How long a key waits when its read-back fails in a way a held stick does not
// explain, before it is sent anyway. See sendCode().
#define UNEXPLAINED_WAIT_US 50000UL

// How long a code stays when the 6502 asks for the ports in the same instant
// it was strobed. See sendCode().
#define READ_GRACE_US 110

// True when the 6502 has asked an encoder that is currently enabled to release
// its port.
static inline bool releaseRequested() {
  return (matrixEnabled && CB2_RELEASE_REQUESTED()) ||
         (ps2Enabled && CA2_RELEASE_REQUESTED());
}

// The two ports, as sendCode() needs them
enum HeldPort : uint8_t { HELD_NONE, HELD_A, HELD_B };

struct EncoderPort {
  volatile uint8_t *ddr;
  volatile uint8_t *port;
  volatile uint8_t *pin;
  uint8_t strobe;   // CA1_STROBE or CB1_STROBE, on PORTD
  HeldPort id;
};

static const EncoderPort PS2_PORT    = { &DDRA, &PORTA, &PINA, CA1_STROBE, HELD_A };
static const EncoderPort MATRIX_PORT = { &DDRB, &PORTB, &PINB, CB1_STROBE, HELD_B };

// The port holding a code, if any, and since when (micros() at its strobe)
HeldPort heldPort = HELD_NONE;
unsigned long heldSince = 0;

// micros() when the firmware last let go of a line it had been driving low
unsigned long releasedAt = 0;

// A queued key that is waiting, per encoder
struct KeyWait {
  bool waiting;
  unsigned long since;       // micros() at the last attempt
  bool unexplained;          // its read-back is failing in a way no stick explains
  unsigned long unexplainedSince;
};

KeyWait ps2Wait = { false, 0, false, 0 };
KeyWait matrixWait = { false, 0, false, 0 };

static inline bool attemptDue(const KeyWait &w) {
  return !w.waiting || (micros() - w.since >= RETRY_INTERVAL_US);
}

// Every line an input with its pull-up on. DDR first: a line the code was
// driving low goes high-impedance (its PORT bit is 0, so no pull-up yet) and
// then the pull-up comes on. It never passes through driven high.
static inline void idlePort(const EncoderPort &p) {
  *p.ddr = 0x00;
  *p.port = 0xFF;
}

// Idle a port that was carrying a code, and note when, so the next sweep
// waits for the released lines to rise (RELEASE_SETTLE_US)
static inline void letGo(const EncoderPort &p) {
  idlePort(p);
  releasedAt = micros();
}

// A full queue keeps the keys it has and drops the new one: the oldest are the
// ones typed first, and losing them would scramble what was typed.
// CircularBuffer's own push() overwrites the oldest instead.
static inline void queueKey(CircularBuffer<uint8_t, BUFFER_SIZE> &queue, uint8_t key) {
  if (!queue.isFull()) {
    queue.push(key);
  }
}

enum SendResult : uint8_t { SEND_DONE, SEND_WAIT, SEND_ABANDONED };

// The lines that held matrix keys will pull low when a code goes out on a
// port. The 64 switches join each row line to each column line, with no
// diodes, so a line the code drives low pulls every line across a held key on
// it low too, and on through further held keys: Shift and ; held together (both
// in row 5) join column 4 to column 0, and a code with column 0 low and column
// 4 high reads back wrong for as long as both are down. Worked out from the
// debounced key state, the same picture the sweep has.
uint8_t matrixPull(bool portB, uint8_t code) {
  uint8_t heldCols[8];
  for (uint8_t row = 0; row < 8; row++) {
    uint8_t cols = 0;
    for (uint8_t col = 0; col < 8; col++) {
      if (matrixKeyState[row][col] >= MATRIX_DEBOUNCE_COUNT) {
        cols |= (uint8_t)(1 << col);
      }
    }
    heldCols[row] = cols;
  }

  uint8_t lowRows = portB ? 0 : (uint8_t)~code;
  uint8_t lowCols = portB ? (uint8_t)~code : 0;
  bool changed = true;
  while (changed) {
    changed = false;
    for (uint8_t row = 0; row < 8; row++) {
      uint8_t rowBit = (uint8_t)(1 << row);
      uint8_t cols = heldCols[row];
      if (!cols) continue;
      if ((lowRows & rowBit) && ((lowCols | cols) != lowCols)) {
        lowCols |= cols;                 // A low row pulls its held keys' columns
        changed = true;
      }
      if (!(lowRows & rowBit) && (lowCols & cols)) {
        lowRows |= rowBit;               // A low column pulls its held keys' rows
        changed = true;
      }
    }
  }
  return portB ? lowCols : lowRows;
}

// Put one key code on a port and strobe it.
//   SEND_DONE       strobed; the caller takes the key off its queue
//   SEND_WAIT       a held stick (or a bridged pair of keys) is pulling one of
//                   the code's 1 bits low; nothing strobed, try again later
//   SEND_ABANDONED  the 6502 asked for the ports first; nothing strobed
//
// A read-back can fail for a reason a held stick (or held keys) do not explain: something
// on the port that is not a switch to ground, such as a joystick with an
// autofire circuit or a bad adapter, pulling or driving lines as the code goes
// out. Waiting for that to clear could take forever, with every key behind it
// stuck and the keyboard dead. So a key waits as long as a stick or held keys
// explain the failure, and otherwise for UNEXPLAINED_WAIT_US, then goes out anyway, as the
// firmware before the read-back sent every key. The 50 ms is five sweeps, long
// enough for the stick masks to catch up with a stick pressed just now.
SendResult sendCode(const EncoderPort &p, uint8_t code, KeyWait &wait) {
  if (releaseRequested()) {
    return SEND_ABANDONED;
  }

  // Decided before the read-back, to keep the interrupts-off stretch short.
  // A 1 read as 0 is explained by a stick holding that line, or by held keys
  // joining it to a line the code drives low.
  // The key walk in matrixPull() takes tens of microseconds, so it is only
  // done when it can matter: here when the key is due to go out anyway, and
  // after a failed read-back below.
  bool sendAnyway = wait.unexplained &&
                    (micros() - wait.unexplainedSince >= UNEXPLAINED_WAIT_US);
  uint8_t held = (p.id == HELD_A) ? joyRowMask : joyColMask;
  if (sendAnyway) {
    held |= matrixPull(p.id == HELD_B, code);
  }

  // Value before direction. While the port is an input, writing PORT only sets
  // pull-ups: the 1 bits keep theirs and the 0 bits lose theirs. Then the 0
  // bits become outputs, driving low. A 1 is never driven.
  *p.port = code;
  *p.ddr = (uint8_t)~code;

  delayMicroseconds(LINE_RISE_US);

  // Read back and strobe with nothing able to run in between, so a switch that
  // closes after the read-back has well under a microsecond to do it in.
  uint8_t sreg = SREG;
  cli();
  if (releaseRequested()) {
    SREG = sreg;
    letGo(p);
    return SEND_ABANDONED;
  }
  uint8_t lines = *p.pin;
  if (lines != code) {
    // A stick or held keys only ever pull a 1 low, and only on lines in held
    bool stickExplains = ((lines & ~code) == 0) && (((code & ~lines) & ~held) == 0);
    if (stickExplains || !sendAnyway) {
      SREG = sreg;
      letGo(p);
      if (!sendAnyway && !stickExplains) {
        // Not yet checked against held keys: do that now, interrupts on
        held |= matrixPull(p.id == HELD_B, code);
        stickExplains = ((lines & ~code) == 0) && (((code & ~lines) & ~held) == 0);
      }
      if (stickExplains) {
        wait.unexplained = false;
      } else if (!wait.unexplained) {
        wait.unexplained = true;
        wait.unexplainedSince = micros();
      }
      return SEND_WAIT;
    }
  }
  PORTD &= ~p.strobe;   // The VIA raises its flag on this edge
  SREG = sreg;

  heldPort = p.id;
  heldSince = micros();
  delayMicroseconds(5);
  PORTD |= p.strobe;

  // A request already here arrived in the same instant as the strobe: in the
  // very 6502 instruction that raised CA2/CB2. With interrupts on, the 6502
  // takes the CA1/CB1 interrupt straight after that instruction, and the
  // Kernal's handler reads the port 77 (CB1) to 86 (CA1) cycles in -- before
  // KBDisable's own wait has begun. Letting go now would hand the handler the
  // released lines, $FF or a stick, as a keystroke. So the code stays until the
  // handler has read it even at 1 MHz, then the port goes.
  //
  // That is up to ~110 us from the request rather than 100, but KBDisable reads
  // no sooner than ~130 us after its request even at 2 MHz, and later still
  // when the handler ran first. A request any later than this cannot follow a
  // strobe with interrupts on -- the 6502 is in the handler -- so only a program
  // that polls with interrupts off meets it, and it is answered at once.
  if (releaseRequested()) {
    while (micros() - heldSince < READ_GRACE_US) {
    }
    endHold();
  }

  return SEND_DONE;
}

// Let the held code go once it has been on the port for CODE_HOLD_US
void serviceHold() {
  if (heldPort != HELD_NONE && (micros() - heldSince >= CODE_HOLD_US)) {
    endHold();
  }
}

void endHold() {
  if (heldPort == HELD_A) {
    letGo(PS2_PORT);
  } else if (heldPort == HELD_B) {
    letGo(MATRIX_PORT);
  }
  heldPort = HELD_NONE;
}

// One attempt at the key at the head of a queue. Returns false if the 6502
// asked for the ports, in which case the caller must service that at once.
bool sendNext(const EncoderPort &p, CircularBuffer<uint8_t, BUFFER_SIZE> &queue,
              KeyWait &wait) {
  switch (sendCode(p, queue.first(), wait)) {
    case SEND_DONE:
      // The PS/2 queue is filled from its clock interrupt, and shift() is not
      // safe against a push() landing half way through it
      ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        queue.shift();
      }
      wait.waiting = false;
      wait.unexplained = false;
      return true;
    case SEND_WAIT:
      wait.waiting = true;
      wait.since = micros();
      return true;
    case SEND_ABANDONED:
    default:
      return false;
  }
}

// ============================================================================
// Keyboard Matrix to ASCII Mapping Table
// ============================================================================
// Maps each matrix position [row][col] to its base ASCII code (no modifiers)
// Special values: 0xFF = no key, 0xFE = modifier key (handled separately)
const uint8_t matrixMap[8][8] PROGMEM = {
  // PA0/Row 0: PB0    PB1    PB2    PB3    PB4    PB5    PB6    PB7
  {             0x60,  0x31,  0x32,  0x33,  0x34,  0x35,  0x36,  0x37 },  // ` 1 2 3 4 5 6 7
  // PA1/Row 1
  {             0x38,  0x39,  0x30,  0x2D,  0x3D,  0x08,  0x1B,  0x09 },  // 8 9 0 - = BS ESC TAB
  // PA2/Row 2
  {             0x51,  0x57,  0x45,  0x52,  0x54,  0x59,  0x55,  0x49 },  // Q W E R T Y U I
  // PA3/Row 3
  {             0x4F,  0x50,  0x5B,  0x5D,  0x5C,  0x1A,  0xFF,  0x41 },  // O P [ ] \ INS (ign) A
  // PA4/Row 4
  {             0x53,  0x44,  0x46,  0x47,  0x48,  0x4A,  0x4B,  0x4C },  // S D F G H J K L
  // PA5/Row 5
  {             0x3B,  0x27,  0x0D,  0x7F,  0xFE,  0x5A,  0x58,  0x43 },  // ; ' ENTER DEL SHIFT Z X C
  // PA6/Row 6
  {             0x56,  0x42,  0x4E,  0x4D,  0x2C,  0x2E,  0x2F,  0x1E },  // V B N M , . / UP
  // PA7/Row 7
  {             0xFE,  0xFF,  0xFF,  0x20,  0xFF,  0x1C,  0x1F,  0x1D }   // CTRL (ign) (ign) SPACE (ign) LEFT DOWN RIGHT
};

void setup() {
  pinMode(VIA_CA1, OUTPUT);
  pinMode(VIA_CA2, INPUT_PULLUP);
  pinMode(VIA_CB1, OUTPUT);
  pinMode(VIA_CB2, INPUT_PULLUP);
  pinMode(PS2CLK, INPUT_PULLUP);
  pinMode(PS2DATA, INPUT_PULLUP);

  digitalWrite(VIA_CA1, HIGH);
  digitalWrite(VIA_CB1, HIGH);

  // Both ports idle as pulled-up inputs from the start, the state the rest of
  // the firmware leaves them in. Out of reset they are bare inputs, which float
  // on a COB or VCS with no helper fitted.
  idlePort(PS2_PORT);
  idlePort(MATRIX_PORT);

  attachInterrupt(digitalPinToInterrupt(PS2CLK), onInterrupt, FALLING);

}

void loop() {
  // Bring both encoders into whatever state CA2/CB2 are asking for, and let a
  // code go once it has been held long enough
  serviceEncoderEnables();
  serviceHold();

  // While a code is held, nothing else touches the ports: not the sweep, which
  // would take them over, and not the other encoder, whose code would reach the
  // held one through any key that is down.
  if (heldPort != HELD_NONE) {
    return;
  }

  // Scan matrix keyboard if enabled. A scan that reports back false was
  // abandoned because the 6502 asked for a port, so service that immediately
  // and start a fresh pass rather than running the output blocks first.
  if (matrixEnabled && !scanMatrix()) {
    serviceEncoderEnables();
    return;
  }

  // PS/2 keyboard output on Port A. A key is only taken off the queue once it
  // has actually been strobed, so one the sticks hold back, or one abandoned
  // because the 6502 asked for the ports, is never lost. One that is waiting
  // does not hold up the other encoder.
  if (ps2Enabled && !ps2Buffer.isEmpty() && attemptDue(ps2Wait)) {
    if (!sendNext(PS2_PORT, ps2Buffer, ps2Wait)) {
      serviceEncoderEnables();
      return;
    }
    if (heldPort != HELD_NONE) {
      return;
    }
  }

  // Matrix keyboard output on Port B
  if (matrixEnabled && !matrixBuffer.isEmpty() && attemptDue(matrixWait)) {
    if (!sendNext(MATRIX_PORT, matrixBuffer, matrixWait)) {
      serviceEncoderEnables();
      return;
    }
  }
}

// Poll CA2/CB2 and bring each encoder into the state the 6502 is asking for.
// Called at the top of loop() and again the moment any longer-running section
// notices a release request, so a port is never held past its budget just
// because the firmware was busy elsewhere.
void serviceEncoderEnables() {
  // Check PS/2 enable/disable (CA2)
  int ps2EnableState = digitalRead(VIA_CA2);
  if (ps2EnableState == LOW && !ps2Enabled) {
    enablePS2();
  } else if (ps2EnableState == HIGH && ps2Enabled) {
    disablePS2();
  }

  // Check matrix enable/disable (CB2)
  int matrixEnableState = digitalRead(VIA_CB2);
  if (matrixEnableState == LOW && !matrixEnabled) {
    enableMatrix();
  } else if (matrixEnableState == HIGH && matrixEnabled) {
    disableMatrix();
  }
}

void enablePS2() {
  // Nothing to set up: Port A idles as pulled-up inputs whether or not the
  // encoder is enabled, and sendCode() takes it only for the length of a code
  ps2Enabled = true;
}

void disablePS2() {
  ps2Enabled = false;

  // Release Port A unconditionally: CA2 going high is the 6502 asking for the
  // port, and it is not conditional on what the matrix is doing. A code held
  // there goes with it.
  //
  // Left with the internal pull-ups on, not bare, because this is exactly the
  // state the 6502 reads the joysticks in. Only the ACE Board carries the 1k
  // port pull-ups itself; on COB and VCS they arrive with a helper board, so a
  // port with nothing fitted would otherwise float and read as noise instead
  // of as an untouched stick. ~30k is far too weak to fight a joystick switch,
  // or a cartridge driving its own matrix rows.
  //
  // Straight at the registers: this is the tail of the release path the 6502
  // waits on, and eight pinMode() calls would add ~36 us to it for no reason.
  if (heldPort == HELD_A) {
    endHold();
  }
  idlePort(PS2_PORT);
}

void enableMatrix() {
  // Nothing to set up here either: both ports idle as pulled-up inputs, and the
  // sweep and sendCode() take them only while they need them.
  matrixEnabled = true;

  // matrixScanRow is deliberately left alone: a sweep abandoned when the 6502
  // took the ports resumes from the row it stopped on, as scanMatrix() intends.
  // Resetting it here undid that resume on every re-enable, so a program that
  // reads a joystick back to back left windows a full sweep never fits in, and
  // no key was ever sent (found on the ACE's AB Controller, which shares this code).
}

void disableMatrix() {
  matrixEnabled = false;

  // Release Port B, with a code held there, left with the internal pull-ups on
  // so the 6502 reads an untouched stick as all-ones even on a board with no
  // external pull-ups fitted (see disablePS2 for both)
  if (heldPort == HELD_B) {
    endHold();
  }
  idlePort(MATRIX_PORT);

  // Release Port A too if PS/2 is not using it. The sweep drives its rows.
  if (!ps2Enabled) {
    idlePort(PS2_PORT);
  }
}

// ============================================================================
// Matrix Keyboard Scanning
// ============================================================================

// Put the ports back to idle when a scan is abandoned part way through. The
// row lines are only ever driven during a scan, and the columns are only ever
// read, so both are always safe to drop.
static inline void abandonScanPorts() {
  idlePort(PS2_PORT);      // Rows
  idlePort(MATRIX_PORT);   // Columns
}

// Scan the keyboard matrix for key presses. Returns false if the sweep was
// abandoned because the 6502 asked for a port back, in which case the caller
// must service that before doing anything else.
bool scanMatrix() {
  // An abandoned sweep resumes from the row it stopped on rather than starting
  // over. That matters because the 6502 now takes the ports every time BASIC
  // evaluates JOY(): a tight polling loop would restart the sweep indefinitely
  // and no keystroke would ever be detected. Resuming also keeps the debounce
  // arithmetic exact -- still one update per key per completed sweep, however
  // many pieces the sweep ended up in.
  if (matrixScanRow == 0) {
    // A line just let go of may not have risen yet (RELEASE_SETTLE_US)
    if (micros() - releasedAt < RELEASE_SETTLE_US) {
      return true;
    }

    // Throttle the *start* of a sweep to MATRIX_SCAN_INTERVAL
    unsigned long currentTime = millis();
    if (currentTime - matrixLastScan < MATRIX_SCAN_INTERVAL) {
      return true;
    }
    matrixLastScan = currentTime;
  }

  // Columns are inputs with their pull-ups for the whole sweep. They already
  // idle that way; this only makes sure of it.
  idlePort(MATRIX_PORT);

  // Phase 1: Scan all rows, update debounce state only.
  //
  // Row and column bits are carried as rolling masks rather than recomputed as
  // (1 << n) each time. The AVR has no barrel shifter, so a variable shift
  // compiles to a loop -- and one inside the eight-column loop cost ~30 us per
  // row, which would have dominated the release latency this whole section
  // exists to bound.
  uint8_t rowBit = (uint8_t)(1 << matrixScanRow);

  for (uint8_t row = matrixScanRow; row < 8; row++, rowBit <<= 1) {
    // Give the port up the moment the 6502 asks for it instead of finishing the
    // sweep first -- this is what bounds the release latency Kernal KBDisable
    // waits on. The checks are spread through the row so that no single stretch
    // of Arduino pin calls can run long between two of them.
    if (releaseRequested()) { matrixScanRow = row; abandonScanPorts(); return false; }

    // Look for the sticks just before reading the row, with no row driven: let
    // every row go, give the lines LINE_RISE_US to settle, and read both ports.
    // With nothing driven a key pulls nothing, so a line low now is a stick's
    // -- held, or bouncing as it closes or opens. Checked once a sweep instead,
    // a switch that bounced between the check and the row read a whole column
    // of keys as pressed (the bench's "= T \ H" with up held).
    DDRA = 0x00;
    PORTA = 0xFF;
    delayMicroseconds(LINE_RISE_US);

    if (releaseRequested()) { matrixScanRow = row; abandonScanPorts(); return false; }

    uint8_t idleRows = PINA;
    uint8_t idleCols = PINB;

    // A row whose PA line JOYSTICK A is holding low reads as every key on that
    // row being pressed. Skip it rather than believe it.
    if (!(idleRows & rowBit)) {
      continue;
    }

    // Drive only the active row LOW; all others high-Z with their pullups off,
    // so no current leaks through pressed keys on inactive rows (ghosting).
    // PORT before DDR, always: enabling the driver first would briefly put the
    // previous contents of PORTA onto lines a joystick may be holding low. Low
    // is the only level a row is ever driven to, so a stick holding that same
    // line is harmless.
    PORTA = 0x00;
    DDRA = rowBit;

    // Small delay to let signals stabilize. Sized for the weak case -- a port
    // with no external pullup fitted, charging the bus through the ~30k
    // internal one -- and it is a physical wait, not an instruction count.
    delayMicroseconds(LINE_RISE_US);

    if (releaseRequested()) { matrixScanRow = row; abandonScanPorts(); return false; }

    // One read gets all eight columns (LOW = pressed, HIGH = not pressed).
    // Both it and the mask are shifted down a bit per iteration so the loop
    // stays constant-time -- see the note above the row loop.
    uint8_t cols = PINB;
    uint8_t colBits = (uint8_t)~idleCols;

    for (uint8_t col = 0; col < 8; col++, cols >>= 1, colBits >>= 1) {
      // A column that was low with no row driven is a stick's (JOYSTICK B,
      // or JOYSTICK A through a held key in its row): every key in it reads
      // as pressed. Leave its keys as they were.
      if (colBits & 1) {
        continue;
      }

      bool pressed = ((cols & 1) == 0);

      // Debounce logic
      if (pressed) {
        if (matrixKeyState[row][col] < MATRIX_DEBOUNCE_COUNT) {
          matrixKeyState[row][col]++;
        }
      } else {
        if (matrixKeyState[row][col] > 0) {
          matrixKeyState[row][col]--;
        }
      }
    }

    // This row's debounce update is complete, so resume from the next one
    if (releaseRequested()) { matrixScanRow = row + 1; abandonScanPorts(); return false; }
  }

  matrixScanRow = 0;  // Sweep complete

  // Release all row lines after scanning, pullups on
  idlePort(PS2_PORT);

  // Phase 2: Update modifier states from current debounce results
  matrixShiftPressed = (matrixKeyState[5][4] >= MATRIX_DEBOUNCE_COUNT);
  matrixCtrlPressed  = (matrixKeyState[7][0] >= MATRIX_DEBOUNCE_COUNT);
  
  // Phase 3: Fire key events with up-to-date modifier state
  for (uint8_t row = 0; row < 8; row++) {
    for (uint8_t col = 0; col < 8; col++) {
      bool keyPressed = (matrixKeyState[row][col] >= MATRIX_DEBOUNCE_COUNT);
      bool keyWasPressed = matrixKeyLast[row][col];
      
      // Detect key press event (transition from not pressed to pressed)
      if (keyPressed && !keyWasPressed) {
        uint8_t ascii = mapMatrixToAscii(row, col);
        if (ascii != 0xFF && ascii != 0xFE) {  // 0xFF = no key, 0xFE = modifier
          queueKey(matrixBuffer, ascii);
        }
      }
      
      matrixKeyLast[row][col] = keyPressed;
    }
  }

  // Phase 4: Work out which lines the joysticks are holding down
  sampleJoystickMasks();

  return true;
}

// ============================================================================
// Joystick Sampling
// ============================================================================

// Work out which of the sixteen port lines the sticks are holding low, with no
// matrix row driven at all: every line is an input with its pullup on, so the
// only thing that can pull one low is a joystick switch. A held key cannot
// register here, because with no row driven both sides of every key switch sit
// at the same potential.
//
// This exists so sendCode() can tell a held stick from anything else when a
// read-back fails; nothing is reported to the 6502, which reads the sticks
// itself under KBDisable. It costs ~10 us once per scan interval, in the idle
// state the ports are left in anyway.
//
// Internal pullups rather than bare inputs, deliberately: only the ACE Board
// carries the 1k port pullups itself. On COB they arrive with the Joystick or
// Keyboard Helper and on VCS with a helper board on the port header, so a
// legitimately assembled machine can have none fitted at all.
void sampleJoystickMasks() {
  idlePort(PS2_PORT);      // JOYSTICK A / matrix rows
  idlePort(MATRIX_PORT);   // JOYSTICK B / matrix columns

  delayMicroseconds(LINE_RISE_US);

  // Switches close to ground, so a line reading low is one being held
  joyRowMask = ~PINA;
  joyColMask = ~PINB;
}

// Map matrix position to ASCII code based on modifiers
uint8_t mapMatrixToAscii(uint8_t row, uint8_t col) {
  // Get base key code from PROGMEM
  uint8_t baseKey = pgm_read_byte(&matrixMap[row][col]);
  
  // Handle special keys
  if (baseKey == 0xFF) return 0xFF;  // No key / ignored
  if (baseKey == 0xFE) return 0xFE;  // Modifier key
  
  // Ctrl takes priority (Shift ignored when Ctrl held)
  if (matrixCtrlPressed) {
    if (baseKey == 0x32) return 0x00;  // Ctrl+2 = NUL
    if (baseKey >= 0x41 && baseKey <= 0x5A) {  // Ctrl+A-Z
      return baseKey - 0x40;  // Convert to 0x01-0x1A
    }
    if (baseKey == 0x5B) return 0x1B;  // Ctrl+[ = ESC
    if (baseKey == 0x5C) return 0x1C;  // Ctrl+\ = FS
    if (baseKey == 0x5D) return 0x1D;  // Ctrl+] = GS
    if (baseKey == 0x36) return 0x1E;  // Ctrl+6 = RS
    if (baseKey == 0x2D) return 0x1F;  // Ctrl+- = US
    return 0xFF;  // Ctrl + unmapped key = no output
  }
  
  // Shift only affects numbers and symbols (not letters)
  if (matrixShiftPressed) {
    if (baseKey == 0x31) return 0x21;  // 1 -> !
    if (baseKey == 0x32) return 0x40;  // 2 -> @
    if (baseKey == 0x33) return 0x23;  // 3 -> #
    if (baseKey == 0x34) return 0x24;  // 4 -> $
    if (baseKey == 0x35) return 0x25;  // 5 -> %
    if (baseKey == 0x36) return 0x5E;  // 6 -> ^
    if (baseKey == 0x37) return 0x26;  // 7 -> &
    if (baseKey == 0x38) return 0x2A;  // 8 -> *
    if (baseKey == 0x39) return 0x28;  // 9 -> (
    if (baseKey == 0x30) return 0x29;  // 0 -> )
    if (baseKey == 0x2D) return 0x5F;  // - -> _
    if (baseKey == 0x3D) return 0x2B;  // = -> +
    if (baseKey == 0x5B) return 0x7B;  // [ -> {
    if (baseKey == 0x5D) return 0x7D;  // ] -> }
    if (baseKey == 0x5C) return 0x7C;  // \ -> |
    if (baseKey == 0x3B) return 0x3A;  // ; -> :
    if (baseKey == 0x27) return 0x22;  // ' -> "
    if (baseKey == 0x60) return 0x7E;  // ` -> ~
    if (baseKey == 0x2C) return 0x3C;  // , -> <
    if (baseKey == 0x2E) return 0x3E;  // . -> >
    if (baseKey == 0x2F) return 0x3F;  // / -> ?
  }
  
  // Return base key (letters are already uppercase in the map)
  return baseKey;
}

// The PS/2 clock's falling edge. Each one is a bit: start, eight data bits
// (least significant first), odd parity, stop.
//
// None of the boards this runs on (the ACE Board, the COB's Keyboard Encoder
// Helper, the VCS Input Board) has pull-ups on the PS/2 lines, only the
// ATmega's own, so the clock line is easily disturbed, and a spike coupled into it looks like a
// falling edge. Counted as a bit, one false edge puts every bit after it one
// place out, and the next bytes decode as other keys or fail parity: at the
// bench about one key in five was lost or turned into a stray character. The
// firmware's port lines no longer being driven high between sweeps is what
// let the spikes through. So three checks, each cheap:
//  - The clock must still be low. A real clock pulse stays low for tens of
//    microseconds; a spike is over before this runs, so it is ignored.
//  - A start bit is 0. An edge with the data line high is not a frame
//    beginning, and the state machine stays where it is.
//  - A stop bit is 1. A frame without one was out of step, and is dropped.
void onInterrupt() {
  static uint8_t bitcount = 0;
  static uint8_t incoming;
  static uint8_t parity;
  static uint32_t prev_ms = 0;
  uint32_t now_ms;
  uint8_t val;

  if (PS2CLK_IS_HIGH()) {
    return;                              // A spike, not a clock pulse
  }

  val = digitalRead(PS2DATA);
  now_ms = millis();

  if (now_ms - prev_ms > 250) { 
    bitcount = 0;
  }

  prev_ms = now_ms;
  bitcount++;

  switch (bitcount) {
    case 1:  // Start bit
      if (val) {                         // Not a start bit: wait for one
        bitcount = 0;
        break;
      }
      incoming = 0;
      parity = 0;
      break;
    case 2:
    case 3:
    case 4:
    case 5:
    case 6:
    case 7:
    case 8:
    case 9:                              // Data bits
      parity += val;                     // Count number of 1 bits
      incoming >>= 1;                    // Right shift one place for next bit
      incoming |= (val) ? 0x80 : 0;      // OR in MSbit
      break;
    case 10:                             // Parity check (PS/2 uses odd parity)
      parity &= 1;                       // Get LSB: 1=odd count, 0=even count
      if (parity == val)                 // For odd parity: bit should be opposite of data parity
        parity = 0xFD;                   // Mark invalid to discard byte
      break;
    case 11: // Stop bit
      if (parity < 0xFD && val) {        // Good parity and a stop bit: save it, otherwise discard
        ps2ToAscii(incoming);            // Convert to ASCII if valid scancode (if full, oldest data lost)
      }
      bitcount = 0;
      break;
    default:
      bitcount = 0;                      // Shouldn't be here so reset state machine
      break;
  }
}

// PS/2 to ASCII conversion function
void ps2ToAscii(uint8_t scancode) {
  // Handle special code prefix
  if (scancode == 0xE0) {
    extendedCodeNext = true;
    return;
  }
  if (scancode == 0xE1) {
    return;
  }

  // Handle break code prefix
  if (scancode == 0xF0) {
    breakCodeNext = true;
    return;
  }
  
  // Handle break codes (key releases)
  if (breakCodeNext) {
    breakCodeNext = false;
    
    // Handle extended keys in break codes
    if (extendedCodeNext) {
      extendedCodeNext = false;
      switch (scancode) {
        case 0x14: // Right Control
          ctrlPressed = false;
          break;
      }
      return;
    }
    
    switch (scancode) {
      case 0x12: // Left Shift
      case 0x59: // Right Shift
        shiftPressed = false;
        break;
      case 0x14: // Control
        ctrlPressed = false;
        break;
    }
    return; // Don't generate ASCII for key releases
  }
  
  // Handle make codes (key presses)
  switch (scancode) {
    case 0x0D: // Tab
      queueKey(ps2Buffer, 0x09);
      return;
    case 0x12: // Left Shift
    case 0x59: // Right Shift
      shiftPressed = true;
      return;
    case 0x14: // Control
      if (extendedCodeNext) {
        extendedCodeNext = false;
      }
      ctrlPressed = true;
      return;
    case 0x5A: // Enter
      if (extendedCodeNext) {
        extendedCodeNext = false;
      }
      queueKey(ps2Buffer, 0x0D);
      return;
    case 0x66: // Backspace
      queueKey(ps2Buffer, 0x08);
      return;
    case 0x6B: // Left Arrow (E0 6B)
      if (extendedCodeNext) {
        extendedCodeNext = false;
        queueKey(ps2Buffer, 0x1C);
      }
      return;
    case 0x70: // Insert (E0 70)
      if (extendedCodeNext) {
        extendedCodeNext = false;
        queueKey(ps2Buffer, 0x1A);
      }
      return;
    case 0x71: // Delete (E0 71)
      if (extendedCodeNext) {
        extendedCodeNext = false;
        queueKey(ps2Buffer, 0x7F);
      }
      return;
    case 0x72: // Down Arrow (E0 72)
      if (extendedCodeNext) {
        extendedCodeNext = false;
        queueKey(ps2Buffer, 0x1F);
      }
      return;
    case 0x74: // Right Arrow (E0 74)
      if (extendedCodeNext) {
        extendedCodeNext = false;
        queueKey(ps2Buffer, 0x1D);
      }
      return;
    case 0x75: // Up Arrow (E0 75)
      if (extendedCodeNext) {
        extendedCodeNext = false;
        queueKey(ps2Buffer, 0x1E);
      }
      return;
    case 0x76: // Escape
      queueKey(ps2Buffer, 0x1B);
      return;
    // Ignored keys: F-keys, Alt, GUI, CapsLock, navigation, keypad
    case 0x01: case 0x03: case 0x04: case 0x05: case 0x06:
    case 0x07: case 0x09: case 0x0A: case 0x0B: case 0x0C:
    case 0x11: case 0x1F: case 0x27: case 0x2F:
    case 0x58: case 0x69: case 0x6C:
    case 0x73: case 0x77: case 0x78: case 0x79:
    case 0x7A: case 0x7B: case 0x7C: case 0x7D: case 0x7E:
    case 0x83:
      extendedCodeNext = false;
      return;
  }

  // If we get here with an extended code, clear the flag and ignore the scancode
  if (extendedCodeNext) {
    extendedCodeNext = false;
    return;
  }

  // Handle control codes
  if (ctrlPressed) {
    switch (scancode) {
      case 0x1E: // 2 or @
        queueKey(ps2Buffer, 0x00); // NULL
        return;
      case 0x1C: // A
        queueKey(ps2Buffer, 0x01); // SOH
        return;
      case 0x32: // B
        queueKey(ps2Buffer, 0x02); // STX
        return;
      case 0x21: // C
        queueKey(ps2Buffer, 0x03); // ETX
        return;
      case 0x23: // D
        queueKey(ps2Buffer, 0x04); // EOT
        return;
      case 0x24: // E
        queueKey(ps2Buffer, 0x05); // ENQ
        return;
      case 0x2B: // F
        queueKey(ps2Buffer, 0x06); // ACK
        return;
      case 0x34: // G
        queueKey(ps2Buffer, 0x07); // BEL
        return;
      case 0x33: // H
        queueKey(ps2Buffer, 0x08); // BS
        return;
      case 0x43: // I
        queueKey(ps2Buffer, 0x09); // HT
        return;
      case 0x3B: // J
        queueKey(ps2Buffer, 0x0A); // LF
        return;
      case 0x42: // K
        queueKey(ps2Buffer, 0x0B); // VT
        return;
      case 0x4B: // L
        queueKey(ps2Buffer, 0x0C); // FF
        return;
      case 0x3A: // M
        queueKey(ps2Buffer, 0x0D); // CR
        return;
      case 0x31: // N
        queueKey(ps2Buffer, 0x0E); // SO
        return;
      case 0x44: // O
        queueKey(ps2Buffer, 0x0F); // SI
        return;
      case 0x4D: // P
        queueKey(ps2Buffer, 0x10); // DLE
        return;
      case 0x15: // Q
        queueKey(ps2Buffer, 0x11); // DC1
        return;
      case 0x2D: // R
        queueKey(ps2Buffer, 0x12); // DC2
        return;
      case 0x1B: // S
        queueKey(ps2Buffer, 0x13); // DC3
        return;
      case 0x2C: // T
        queueKey(ps2Buffer, 0x14); // DC4
        return;
      case 0x3C: // U
        queueKey(ps2Buffer, 0x15); // NAK
        return;
      case 0x2A: // V
        queueKey(ps2Buffer, 0x16); // SYN
        return;
      case 0x1D: // W
        queueKey(ps2Buffer, 0x17); // ETB
        return;
      case 0x22: // X
        queueKey(ps2Buffer, 0x18); // CAN
        return;
      case 0x35: // Y
        queueKey(ps2Buffer, 0x19); // EM
        return;
      case 0x1A: // Z
        queueKey(ps2Buffer, 0x1A); // SUB
        return;
      case 0x54: // [
        queueKey(ps2Buffer, 0x1B); // ESC
        return;
      case 0x5D: // "\"
        queueKey(ps2Buffer, 0x1C); // FS (LEFT)
        return;
      case 0x5B: // ]
        queueKey(ps2Buffer, 0x1D); // GS (RIGHT)
        return;
      case 0x36: // 6 or ^
        queueKey(ps2Buffer, 0x1E); // RS (UP)
        return;
      case 0x4E: // - or _
        queueKey(ps2Buffer, 0x1F); // US (DOWN)
        return;
    }
    return;
  }
  
  // Regular character mapping
  static const char unshifted[] = {
    0,   0,   0,   0,   0,   0,   0,   0,     // 0x00-0x07
    0,   0,   0,   0,   0,   0, '`',   0,     // 0x08-0x0F
    0,   0,   0,   0,   0, 'Q', '1',   0,     // 0x10-0x17
    0,   0, 'Z', 'S', 'A', 'W', '2',   0,     // 0x18-0x1F
    0, 'C', 'X', 'D', 'E', '4', '3',   0,     // 0x20-0x27
    0, ' ', 'V', 'F', 'T', 'R', '5',   0,     // 0x28-0x2F
    0, 'N', 'B', 'H', 'G', 'Y', '6',   0,     // 0x30-0x37
    0,   0, 'M', 'J', 'U', '7', '8',   0,     // 0x38-0x3F
    0, ',', 'K', 'I', 'O', '0', '9',   0,     // 0x40-0x47
    0, '.', '/', 'L', ';', 'P', '-',   0,     // 0x48-0x4F
    0,   0,'\'',   0, '[', '=',   0,   0,     // 0x50-0x57
    0,   0,   0, ']',   0,'\\',   0,   0,     // 0x58-0x5F
  };
  
  static const char shifted[] = {
    0,   0,   0,   0,   0,   0,   0,   0,     // 0x00-0x07
    0,   0,   0,   0,   0,   0, '~',   0,     // 0x08-0x0F
    0,   0,   0,   0,   0, 'Q', '!',   0,     // 0x10-0x17
    0,   0, 'Z', 'S', 'A', 'W', '@',   0,     // 0x18-0x1F
    0, 'C', 'X', 'D', 'E', '$', '#',   0,     // 0x20-0x27
    0, ' ', 'V', 'F', 'T', 'R', '%',   0,     // 0x28-0x2F
    0, 'N', 'B', 'H', 'G', 'Y', '^',   0,     // 0x30-0x37
    0,   0, 'M', 'J', 'U', '&', '*',   0,     // 0x38-0x3F
    0, '<', 'K', 'I', 'O', ')', '(',   0,     // 0x40-0x47
    0, '>', '?', 'L', ':', 'P', '_',   0,     // 0x48-0x4F
    0,   0, '"',   0, '{', '+',   0,   0,     // 0x50-0x57
    0,   0,   0, '}',   0, '|',   0,   0,     // 0x58-0x5F
  };
  
  // Check if scancode is within our mapping range
  if (scancode >= sizeof(unshifted)) {
    return; // Unknown scancode
  }
  
  char result;
  
  // Get character (letters are always uppercase in both tables)
  if (shiftPressed) {
    result = shifted[scancode];
  } else {
    result = unshifted[scancode];
  }
  
  if (result != 0) {
    queueKey(ps2Buffer, result);
  }
}
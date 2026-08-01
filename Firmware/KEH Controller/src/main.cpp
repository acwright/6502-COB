#define CIRCULAR_BUFFER_INT_SAFE

#include <Arduino.h>
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

// ATMega1284 PORT A / 6522 VIA PORT A
#define VIA_PA0 24
#define VIA_PA1 25
#define VIA_PA2 26
#define VIA_PA3 27
#define VIA_PA4 28
#define VIA_PA5 29
#define VIA_PA6 30
#define VIA_PA7 31

// ATMega1284 PORT B / 6522 VIA PORT B
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
// itself: Kernal KBDisable takes both encoders offline, this ATmega goes
// high-impedance, and the 6502 reads the raw ports with the sticks the only
// things pulling on them. That is the same arrangement a C64 has, it needs no
// wire protocol, and it is the only way both sticks can be read reliably --
// anything this encoder drives onto a port is fighting the switches wired to
// those same eight lines.
//
// What the firmware does need is to know which lines a stick is holding down.
// A held signal pins its line low for as long as it is held, and every key
// along that row or column then reads as pressed. These masks keep the sticks
// out of the matrix scan.
uint8_t joyRowMask = 0;   // PA lines JOYSTICK A is holding low -> unscannable rows
uint8_t joyColMask = 0;   // PB lines JOYSTICK B is holding low -> unscannable columns

void onInterrupt();
void enablePS2();
void disablePS2();
void enableMatrix();
void disableMatrix();
void ps2ToAscii(uint8_t scancode);
bool scanMatrix();
uint8_t mapMatrixToAscii(uint8_t row, uint8_t col);
void serviceEncoderEnables();
bool settleBetweenCharacters();
bool matrixRowConflict();
bool writePortA(uint8_t value);
bool writePortB(uint8_t value);
void sampleJoystickMasks();

// ============================================================================
// VIA Port Access
// ============================================================================
// On the MightyCore "standard" pinout VIA_PA0-PA7 are D24-D31, which is exactly
// ATmega PORTA bits 0-7, and VIA_PB0-PB7 are D0-D7, which is exactly PORTB bits
// 0-7. Nothing else on this board lives on either register, so the whole port
// can be manipulated in a single instruction.
//
// That matters in two places. The encoder must let go of a port within 100 us
// of being asked, because that is how the 6502 reads the joysticks at all and
// Kernal KBDisable waits exactly that long before reading. So the release path
// has to be effectively instantaneous, and the scan loop has to be able to
// check for a release request without paying ~4 us per Arduino call.
// Everything that is not on that path keeps using pinMode/digitalRead.
//
// If the VIA_Px pin defines above ever change, these must change with them.

// CA2 (PD1) and CB2 (PD5) are the 6502 asking for a port back, active high.
#define CA2_RELEASE_REQUESTED() (PIND & _BV(PD1))
#define CB2_RELEASE_REQUESTED() (PIND & _BV(PD5))

// True when the 6502 has asked an encoder that is currently enabled -- and so
// currently driving a port -- to release it.
static inline bool releaseRequested() {
  return (matrixEnabled && CB2_RELEASE_REQUESTED()) ||
         (ps2Enabled && CA2_RELEASE_REQUESTED());
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
  
  attachInterrupt(digitalPinToInterrupt(PS2CLK), onInterrupt, FALLING);
}

void loop() {
  // Bring both encoders into whatever state CA2/CB2 are asking for
  serviceEncoderEnables();

  // Scan matrix keyboard if enabled. A scan that reports back false was
  // abandoned because the 6502 asked for a port, so service that immediately
  // and start a fresh pass rather than running the output blocks first.
  if (matrixEnabled && !scanMatrix()) {
    serviceEncoderEnables();
    return;
  }

  // Handle PS/2 keyboard output on Port A. The character is only consumed once
  // it has actually been strobed, so one abandoned mid-write cannot be lost.
  if (ps2Enabled && !ps2Buffer.isEmpty()) {
    if (!writePortA(ps2Buffer.first())) {
      serviceEncoderEnables();
      return;
    }
    ps2Buffer.shift();
    if (!settleBetweenCharacters()) {
      serviceEncoderEnables();
      return;
    }
  }

  // Handle matrix keyboard output on Port B
  if (matrixEnabled && !matrixBuffer.isEmpty() && !matrixRowConflict()) {
    if (!writePortB(matrixBuffer.first())) {
      serviceEncoderEnables();
      return;
    }
    matrixBuffer.shift();
    if (!settleBetweenCharacters()) {
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

// The settle gap the 6502 needs between strobes. Spent in short slices with a
// release check between each, rather than blocking for the whole 100 us, so a
// request arriving just after a strobe is still answered on time. Returns false
// if one arrived, in which case the caller must stop what it is doing.
bool settleBetweenCharacters() {
  for (uint8_t i = 0; i < 10; i++) {
    if (releaseRequested()) {
      return false;
    }
    delayMicroseconds(10);
  }
  return true;
}

// When two keys on the same row are held simultaneously, their switches bridge
// Port B columns through the shared row wire.  This corrupts anything driven on
// Port B because the ATmega's output drivers fight each other through that
// path.  Output is deferred until no row has multiple pressed keys.
bool matrixRowConflict() {
  for (uint8_t row = 0; row < 8; row++) {
    uint8_t count = 0;
    for (uint8_t col = 0; col < 8; col++) {
      if (matrixKeyState[row][col] >= MATRIX_DEBOUNCE_COUNT) {
        if (++count >= 2) {
          return true;
        }
      }
    }
  }
  return false;
}

// Drive a byte onto Port A and strobe CA1. Matrix scanning parks the row lines
// as inputs, so the direction has to be re-asserted on every write.
//
// Returns false if the 6502 asked for the port before the strobe went out, in
// which case nothing was signalled and the caller must keep the byte queued.
// This matters more than it looks: BASIC evaluating JOY() disables the encoders
// every time, so a release landing in the middle of a character write is a
// routine event rather than a rarity. Strobing a port that is about to be
// released would leave the 6502's ISR reading joystick lines and buffering them
// as a keystroke.
bool writePortA(uint8_t value) {
  // Nothing has been committed to the wire yet, so bail before touching the
  // port at all if the 6502 has already asked for it
  if (releaseRequested()) {
    return false;
  }

  // Value before direction: while the port is still an input this only sets
  // pullups, so the byte is never half-driven on its way out
  PORTA = value;
  DDRA = 0xFF;

  if (releaseRequested()) {
    return false;
  }

  digitalWrite(VIA_CA1, LOW); // Signal that data is ready
  delayMicroseconds(5);
  digitalWrite(VIA_CA1, HIGH);
  return true;
}

// Drive a byte onto Port B and strobe CB1. Port A (the row lines) is parked
// high-impedance first, so a single pressed key cannot short a driven column
// back into a driven row through its switch. Returns false without strobing if
// the 6502 asked for the port first -- see writePortA.
bool writePortB(uint8_t value) {
  if (releaseRequested()) {
    return false;
  }

  // Park the row lines as pulled-up inputs first
  DDRA = 0x00;
  PORTA = 0xFF;

  // Value before direction -- see writePortA
  PORTB = value;
  DDRB = 0xFF;

  if (releaseRequested()) {
    return false;
  }

  digitalWrite(VIA_CB1, LOW); // Signal that data is ready
  delayMicroseconds(5);
  digitalWrite(VIA_CB1, HIGH);
  return true;
}

void enablePS2() {
  ps2Enabled = true;

  // Set Port A as output for PS/2 data. PORTA already reads 0xFF from the
  // released state, so the lines idle high rather than briefly presenting
  // whatever was last driven.
  DDRA = 0xFF;
}

void disablePS2() {
  ps2Enabled = false;

  // Release Port A unconditionally: CA2 going high is the 6502 asking for the
  // port, and it is not conditional on what the matrix is doing. scanMatrix()
  // drives the row lines itself and parks them between passes, so there is
  // nothing here worth preserving for it -- whereas the old `if (!matrixEnabled)`
  // guard meant that with the matrix enabled this path never let go of Port A
  // at all.
  //
  // Parked with the internal pullups on, not bare, because this is exactly the
  // state the 6502 reads the joysticks in. Only the ACE Board carries the 1k
  // port pullups itself; on COB and VCS they arrive with a helper board, so a
  // port with nothing fitted would otherwise float and read as noise instead of
  // as an untouched stick. ~30k is far too weak to fight a joystick switch, or
  // a cartridge driving its own matrix rows.
  //
  // Straight at the registers: this is the tail of the release path the 6502
  // waits on, and eight pinMode() calls would add ~36 us to it for no reason.
  DDRA = 0x00;
  PORTA = 0xFF;
}

void enableMatrix() {
  matrixEnabled = true;

  // Port B carries column reading and data output; idle driving high
  PORTB = 0xFF;
  DDRB = 0xFF;

  // Port A is left as pulled-up inputs rather than driven. scanMatrix() takes
  // it a row at a time and writePortB() parks it, so nothing here needs it as
  // an output -- and driving it would put either all rows high against a
  // joystick holding one low, or all rows low against the columns.
  if (!ps2Enabled) {
    DDRA = 0x00;
    PORTA = 0xFF;
  }

  // Start a fresh sweep rather than resuming one abandoned before the matrix
  // was last disabled
  matrixScanRow = 0;
}

void disableMatrix() {
  matrixEnabled = false;

  // Release Port B, parked with the internal pullups on so the 6502 reads an
  // untouched stick as all-ones even on a board with no external pullups
  // fitted, and straight at the registers so the release is immediate (see
  // disablePS2 for both).
  DDRB = 0x00;
  PORTB = 0xFF;

  // Release Port A too if PS/2 is not using it
  if (!ps2Enabled) {
    DDRA = 0x00;
    PORTA = 0xFF;
  }
}

// ============================================================================
// Matrix Keyboard Scanning
// ============================================================================

// Put the ports back where the rest of the firmware expects them when a scan is
// abandoned part way through. The row lines are only ever driven during a scan
// so they are always safe to drop; the columns are only released if Port B is
// what the 6502 actually asked for, otherwise they go back to idling high.
static inline void abandonScanPorts() {
  DDRA = 0x00;    // Rows -> input, pullups on
  PORTA = 0xFF;

  if (CB2_RELEASE_REQUESTED()) {
    DDRB = 0x00;  // Columns -> input, pullups on; the 6502 wants Port B
    PORTB = 0xFF;
  } else {
    PORTB = 0xFF; // Columns -> back to driving idle high
    DDRB = 0xFF;
  }
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
    // Throttle the *start* of a sweep to MATRIX_SCAN_INTERVAL
    unsigned long currentTime = millis();
    if (currentTime - matrixLastScan < MATRIX_SCAN_INTERVAL) {
      return true;
    }
    matrixLastScan = currentTime;
  }

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

    // A row whose PA line JOYSTICK A is holding low reads as every key on that
    // row being pressed. Skip those rows rather than believe them -- this is
    // where the phantom keystrokes came from.
    if (joyRowMask & rowBit) {
      continue;
    }

    // Drive only the active row LOW; all others high-Z with their pullups off,
    // so no current leaks through pressed keys on inactive rows (ghosting).
    // PORT before DDR, always: enabling the driver first would briefly put the
    // previous contents of PORTA onto lines a joystick may be holding low.
    PORTA = 0x00;
    DDRA = rowBit;

    if (releaseRequested()) { matrixScanRow = row; abandonScanPorts(); return false; }

    // Columns to inputs with pullups for reading
    DDRB = 0x00;
    PORTB = 0xFF;

    // Small delay to let signals stabilize. Sized for the weak case -- a port
    // with no external pullup fitted, charging the bus through the ~30k
    // internal one -- and it is a physical wait, not an instruction count.
    delayMicroseconds(10);

    if (releaseRequested()) { matrixScanRow = row; abandonScanPorts(); return false; }

    // One read gets all eight columns (LOW = pressed, HIGH = not pressed).
    // Both it and the mask are shifted down a bit per iteration so the loop
    // stays constant-time -- see the note above the row loop.
    uint8_t cols = PINB;
    uint8_t colBits = joyColMask;

    for (uint8_t col = 0; col < 8; col++, cols >>= 1, colBits >>= 1) {
      // A column JOYSTICK B is holding low reads as every key in it being
      // pressed, exactly as a held row does. Skip those too.
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

    // Restore columns to driving idle high, ready for data transmission
    PORTB = 0xFF;
    DDRB = 0xFF;
  }

  matrixScanRow = 0;  // Sweep complete

  // Release all row lines after scanning, pullups on
  DDRA = 0x00;
  PORTA = 0xFF;

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
          matrixBuffer.push(ascii);
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
// This exists solely to keep the sticks out of the matrix scan; nothing is
// reported to the 6502, which reads the sticks itself under KBDisable. It
// piggybacks on a window the firmware already opens -- scanMatrix() puts Port B
// into INPUT_PULLUP and back eight times a sweep already -- so it adds no new
// class of port disturbance, and costs ~10 us once per scan interval.
//
// Internal pullups rather than bare inputs, deliberately: only the ACE Board
// carries the 1k port pullups itself. On COB they arrive with the Joystick or
// Keyboard Helper and on VCS with a helper board on the port header, so a
// legitimately assembled machine can have none fitted at all.
void sampleJoystickMasks() {
  DDRA = 0x00;   // JOYSTICK A / matrix rows    -> input, pullups on
  PORTA = 0xFF;
  DDRB = 0x00;   // JOYSTICK B / matrix columns -> input, pullups on
  PORTB = 0xFF;

  delayMicroseconds(10);

  // Switches close to ground, so a line reading low is one being held
  joyRowMask = ~PINA;
  joyColMask = ~PINB;

  // Rows stay parked as pulled-up inputs; columns go back to driving idle high,
  // which is the state the rest of the firmware expects between sweeps.
  PORTB = 0xFF;
  DDRB = 0xFF;
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

void onInterrupt() {
  static uint8_t bitcount = 0;
  static uint8_t incoming;
  static uint8_t parity;
  static uint32_t prev_ms = 0;
  uint32_t now_ms;
  uint8_t val;

  val = digitalRead(PS2DATA);
  now_ms = millis();

  if (now_ms - prev_ms > 250) { 
    bitcount = 0;
  }

  prev_ms = now_ms;
  bitcount++;

  switch (bitcount) {
    case 1:  // Start bit
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
      if (parity < 0xFD) {               // Good so save byte in buffer, otherwise discard
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
      ps2Buffer.push(0x09);
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
      ps2Buffer.push(0x0D);
      return;
    case 0x66: // Backspace
      ps2Buffer.push(0x08);
      return;
    case 0x6B: // Left Arrow (E0 6B)
      if (extendedCodeNext) {
        extendedCodeNext = false;
        ps2Buffer.push(0x1C);
      }
      return;
    case 0x70: // Insert (E0 70)
      if (extendedCodeNext) {
        extendedCodeNext = false;
        ps2Buffer.push(0x1A);
      }
      return;
    case 0x71: // Delete (E0 71)
      if (extendedCodeNext) {
        extendedCodeNext = false;
        ps2Buffer.push(0x7F);
      }
      return;
    case 0x72: // Down Arrow (E0 72)
      if (extendedCodeNext) {
        extendedCodeNext = false;
        ps2Buffer.push(0x1F);
      }
      return;
    case 0x74: // Right Arrow (E0 74)
      if (extendedCodeNext) {
        extendedCodeNext = false;
        ps2Buffer.push(0x1D);
      }
      return;
    case 0x75: // Up Arrow (E0 75)
      if (extendedCodeNext) {
        extendedCodeNext = false;
        ps2Buffer.push(0x1E);
      }
      return;
    case 0x76: // Escape
      ps2Buffer.push(0x1B);
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
        ps2Buffer.push(0x00); // NULL
        return;
      case 0x1C: // A
        ps2Buffer.push(0x01); // SOH
        return;
      case 0x32: // B
        ps2Buffer.push(0x02); // STX
        return;
      case 0x21: // C
        ps2Buffer.push(0x03); // ETX
        return;
      case 0x23: // D
        ps2Buffer.push(0x04); // EOT
        return;
      case 0x24: // E
        ps2Buffer.push(0x05); // ENQ
        return;
      case 0x2B: // F
        ps2Buffer.push(0x06); // ACK
        return;
      case 0x34: // G
        ps2Buffer.push(0x07); // BEL
        return;
      case 0x33: // H
        ps2Buffer.push(0x08); // BS
        return;
      case 0x43: // I
        ps2Buffer.push(0x09); // HT
        return;
      case 0x3B: // J
        ps2Buffer.push(0x0A); // LF
        return;
      case 0x42: // K
        ps2Buffer.push(0x0B); // VT
        return;
      case 0x4B: // L
        ps2Buffer.push(0x0C); // FF
        return;
      case 0x3A: // M
        ps2Buffer.push(0x0D); // CR
        return;
      case 0x31: // N
        ps2Buffer.push(0x0E); // SO
        return;
      case 0x44: // O
        ps2Buffer.push(0x0F); // SI
        return;
      case 0x4D: // P
        ps2Buffer.push(0x10); // DLE
        return;
      case 0x15: // Q
        ps2Buffer.push(0x11); // DC1
        return;
      case 0x2D: // R
        ps2Buffer.push(0x12); // DC2
        return;
      case 0x1B: // S
        ps2Buffer.push(0x13); // DC3
        return;
      case 0x2C: // T
        ps2Buffer.push(0x14); // DC4
        return;
      case 0x3C: // U
        ps2Buffer.push(0x15); // NAK
        return;
      case 0x2A: // V
        ps2Buffer.push(0x16); // SYN
        return;
      case 0x1D: // W
        ps2Buffer.push(0x17); // ETB
        return;
      case 0x22: // X
        ps2Buffer.push(0x18); // CAN
        return;
      case 0x35: // Y
        ps2Buffer.push(0x19); // EM
        return;
      case 0x1A: // Z
        ps2Buffer.push(0x1A); // SUB
        return;
      case 0x54: // [
        ps2Buffer.push(0x1B); // ESC
        return;
      case 0x5D: // "\"
        ps2Buffer.push(0x1C); // FS (LEFT)
        return;
      case 0x5B: // ]
        ps2Buffer.push(0x1D); // GS (RIGHT)
        return;
      case 0x36: // 6 or ^
        ps2Buffer.push(0x1E); // RS (UP)
        return;
      case 0x4E: // - or _
        ps2Buffer.push(0x1F); // US (DOWN)
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
    ps2Buffer.push(result);
  }
}
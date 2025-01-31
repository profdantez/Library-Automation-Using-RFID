#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 5
#define BUZZER_PIN 9  // Pin connected to the buzzer

MFRC522 rfid(SS_PIN, RST_PIN);  // Instance of the MFRC522 class

// List of known tags (replace with your actual known tag values)
byte knownTags[3][4] = {
  {92, 27, 200, 51}, // Example tag 1
  {250, 212, 22, 63},  // Example tag 2
  {250, 203, 72, 179}
};
const int KnownTagCount = 3;

void setup() {
  Serial.begin(9600);  // Start the serial communication
  SPI.begin();         // Init SPI bus
  rfid.PCD_Init();     // Init MFRC522
  pinMode(BUZZER_PIN, OUTPUT);  // Set buzzer pin as OUTPUT
  Serial.println("Place your card on the reader...");
}

void loop() {
  // Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
  if (!rfid.PICC_IsNewCardPresent())
    return;

  // Verify if the NUID has been read
  if (!rfid.PICC_ReadCardSerial())
    return;

  printDec(rfid.uid.uidByte, rfid.uid.size);
  Serial.println();
  
  // Check if the scanned tag is known
  if (!isKnownTag(rfid.uid.uidByte)) {
//    Serial.println("Unknown tag detected!");
    soundBuzzer();
  } 

  // Halt PICC
  rfid.PICC_HaltA();

  // Stop encryption on PCD
  rfid.PCD_StopCrypto1();
}

// Function to check if the scanned tag is in the list of known tags
bool isKnownTag(byte *tag) {
  for (int i = 0; i < KnownTagCount; i++) {
    bool match = true;
    for (int j = 0; j < 4; j++) {
      if (knownTags[i][j] != tag[j]) {
        match = false;
        break;
      }
    }
    if (match)
      return true;
  }
  return false;
}



// Function to sound the buzzer
void soundBuzzer() {
  digitalWrite(BUZZER_PIN, HIGH);  // Turn the buzzer on
  delay(1000);                     // Keep the buzzer on for 1 second
  digitalWrite(BUZZER_PIN, LOW);   // Turn the buzzer off
}

/**
 * Helper function to print a byte array in decimal format.
 */
void printDec(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(' ');
    Serial.print(buffer[i], DEC);
  }
}

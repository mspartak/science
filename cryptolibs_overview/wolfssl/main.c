#include <stdio.h>
#include <wolfssl/wolfcrypt/types.h>
#include <wolfssl/wolfcrypt/wc_port.h>
#include <wolfssl/wolfcrypt/aes.h>

/* AES key size */
#define AES_KEY_SIZE   (AES_128_KEY_SIZE)

/* AES data blocks count */
#define AES_DATA_BLOCKS (2)

int    ret;     /* returned value */
/* Buffer to store ciphertext (2 AES blocks) */
byte   ciphertext[ AES_DATA_BLOCKS * AES_BLOCK_SIZE];
/* Buffer to store decrypted data (2 AES blocks) */
byte   plaintext[ AES_DATA_BLOCKS * AES_BLOCK_SIZE];

/* ===========================================================================================================
 * Test vector details:
 * ----- Filename: OFBMMT128.rsp ------
 * from https://csrc.nist.gov/projects/cryptographic-algorithm-validation-program/block-ciphers
 *
 * COUNT = 2
 * KEY = 7a70cc6b261eeccb05c57117d5763197
 * IV = bb7b9667fbd76d5ee204828769a341b1
 * PLAINTEXT = 823cbaae3760c85512a3c83fd60bb54b7cfc739b295b63e05ef435d86e19fd15368c89ff08a0f21ce89a728ffb5d75df
 * CIPHERTEXT = f5c49aae8a026bf05e525a12ab7e195eea8a1b71a8d32a5113aa8974858f2cfc0339805003a0cb1a7be19f376d4604eb
 =========================================================================================================== */

/* Test vector converted to C format */
byte key[AES_KEY_SIZE] = {0x7a,0x70,0xcc,0x6b,0x26,0x1e,0xec,0xcb,0x5,0xc5,0x71,0x17,0xd5,0x76,0x31,0x97};
byte iv[]              = {0xbb,0x7b,0x96,0x67,0xfb,0xd7,0x6d,0x5e,0xe2,0x4,0x82,0x87,0x69,0xa3,0x41,0xb1};
byte nist_plaintext[]  = {0x82,0x3c,0xba,0xae,0x37,0x60,0xc8,0x55,0x12,0xa3,0xc8,0x3f,0xd6,0xb,0xb5,0x4b,0x7c,0xfc,0x73,0x9b,0x29,0x5b,0x63,0xe0,0x5e,0xf4,0x35,0xd8,0x6e,0x19,0xfd,0x15};
byte nist_ciphertext[] = {0xf5,0xc4,0x9a,0xae,0x8a,0x2,0x6b,0xf0,0x5e,0x52,0x5a,0x12,0xab,0x7e,0x19,0x5e,0xea,0x8a,0x1b,0x71,0xa8,0xd3,0x2a,0x51,0x13,0xaa,0x89,0x74,0x85,0x8f,0x2c,0xfc};

/* Function to print byte values in HEX format */
void PrintHex(unsigned char * buffer,
              size_t buf_size)
{
    for (size_t n = 0; n < buf_size; n++)
    {
        printf("%02X", buffer[n]);
    }
    printf("\n");
}

/* Function to demonstrate AES-OFB encryption */
void AesEncryptionDemo(void)
{
    Aes enc_aes;

    wc_AesInit(&enc_aes,
               NULL,
               INVALID_DEVID);

    wc_AesSetKey(&enc_aes,
                       key,
                       AES_KEY_SIZE,
                       iv,
                       AES_ENCRYPTION);
    if (ret != 0)
        printf("ERROR in wc_AesSetKey\n");

    /* Encrypt block #1 */
    ret = wc_AesOfbEncrypt(&enc_aes,
                           ciphertext,
                           nist_plaintext,
                           AES_BLOCK_SIZE);
    if (ret != 0)
        printf("ERROR during encryption!\n");

    printf("Encrypted block #1 using AES-OFB: \n");
    PrintHex(ciphertext, AES_BLOCK_SIZE);

    /* Encrypt block #2 */
    ret = wc_AesOfbEncrypt(&enc_aes,
                           &ciphertext[AES_BLOCK_SIZE],
                           &nist_plaintext[AES_BLOCK_SIZE],
                           AES_BLOCK_SIZE);
    if (ret != 0)
        printf("ERROR during encryption!\n");

    printf("Encrypted block #2 using AES-OFB: \n");
    PrintHex(&ciphertext[AES_BLOCK_SIZE], AES_BLOCK_SIZE);

    wc_AesFree(&enc_aes);
}


/* Function to demonstrate AES-OFB encryption (very simple)  */
void AesEncryptionDemo_Simple(void)
{
    Aes enc_aes;

    wc_AesInit(&enc_aes,
               NULL,
               INVALID_DEVID);
    ret = wc_AesSetKey(&enc_aes,
                       key,
                       AES_KEY_SIZE,
                       iv,
                       AES_ENCRYPTION);
    /* Encrypt block #1 */
    wc_AesOfbEncrypt(&enc_aes,
                     ciphertext,
                     nist_plaintext,
                     sizeof(ciphertext));
    printf("Encrypted using AES-OFB: \n");
    PrintHex(ciphertext, sizeof(ciphertext));
}

/* Function to demonstrate AES-OFB deccryption */
void AesDecryptionDemo(void)
{
    Aes dec_aes;

    if (wc_AesInit(&dec_aes,
                   NULL,
                   INVALID_DEVID) != 0) {
        printf("ERROR during AES initialization!\n");
    }

    /* Note: AES-OFB uses AES_ENCRYPTION for decryption. */
    ret = wc_AesSetKey(&dec_aes,
                       key,
                       AES_KEY_SIZE,
                       iv,
                       AES_ENCRYPTION);
    if (ret != 0)
        printf("ERROR in wc_AesSetKey\n");

    /* Encrypt block #1 */
    ret = wc_AesOfbDecrypt(&dec_aes,
                           plaintext,
                           ciphertext,
                           AES_BLOCK_SIZE);
    if (ret != 0)
        printf("ERROR during decryption!\n");

    printf("Decrypted block #1 using AES-OFB: \n");
    PrintHex(plaintext, AES_BLOCK_SIZE);

    /* Encrypt block #2 */
    ret = wc_AesOfbEncrypt(&dec_aes,
                           &plaintext[AES_BLOCK_SIZE],
                           &ciphertext[AES_BLOCK_SIZE],
                           AES_BLOCK_SIZE);
    if (ret != 0)
        printf("ERROR during decryption!\n");

    printf("Decrypted block #2 using AES-OFB: \n");
    PrintHex(&plaintext[AES_BLOCK_SIZE], AES_BLOCK_SIZE);

    wc_AesFree(&dec_aes);
}

int main()
{
    printf("Hello World!\n");

    if ((ret = wolfCrypt_Init()) != 0) {
        printf("wolfCrypt_Init failed %d\n", (int)ret);
    }

    printf("AES key: \n");
    PrintHex(key, AES_KEY_SIZE);
    printf("NIST plaintext: \n");
    PrintHex(nist_plaintext, AES_DATA_BLOCKS * AES_BLOCK_SIZE);
    printf("NIST ciphertext: \n");
    PrintHex(nist_ciphertext, AES_DATA_BLOCKS * AES_BLOCK_SIZE);

    printf("======== AES encryption ======== \n");    
    AesEncryptionDemo();

    printf("======== AES decryption ======== \n");
    AesDecryptionDemo();

    printf("======== AES encryption (simplified version) ======== \n");
    AesEncryptionDemo_Simple();

    printf("completed\n");

    return 0;
}

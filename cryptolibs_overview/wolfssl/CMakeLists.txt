cmake_minimum_required(VERSION 3.5)

project(qt_hello LANGUAGES C)

# Set relative path to the wolfSSL sources
set(WOLFCRYPT_SRC_PATH ../wolfssl-5.6.6/wolfcrypt/src)

# Add compile definitions
add_compile_definitions(WOLFCRYPT_ONLY) # Only WolfCrypt compiled
add_compile_definitions(WOLFSSL_KEY_GEN) # Enable Keys Generation
add_compile_definitions(WOLFSSL_AES_OFB, WOLFSSL_AES_DIRECT) # Enable AES-OFB operations

include_directories("../wolfssl-5.6.6") # Check your version of wolfssl

add_executable(qt_hello
               main.c
               ${WOLFCRYPT_SRC_PATH}/asn.c
               ${WOLFCRYPT_SRC_PATH}/wc_port.c
               ${WOLFCRYPT_SRC_PATH}/aes.c
               ${WOLFCRYPT_SRC_PATH}/coding.c
               ${WOLFCRYPT_SRC_PATH}/des3.c
               ${WOLFCRYPT_SRC_PATH}/hmac.c
               ${WOLFCRYPT_SRC_PATH}/pwdbased.c
               ${WOLFCRYPT_SRC_PATH}/memory.c
               ${WOLFCRYPT_SRC_PATH}/sp_int.c
               ${WOLFCRYPT_SRC_PATH}/hash.c
               ${WOLFCRYPT_SRC_PATH}/md5.c
               ${WOLFCRYPT_SRC_PATH}/sha.c
               ${WOLFCRYPT_SRC_PATH}/sha256.c
               ${WOLFCRYPT_SRC_PATH}/wc_encrypt.c
               ${WOLFCRYPT_SRC_PATH}/rsa.c
               ${WOLFCRYPT_SRC_PATH}/dsa.c
               ${WOLFCRYPT_SRC_PATH}/random.c
           )

include(GNUInstallDirs)
install(TARGETS qt_hello
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

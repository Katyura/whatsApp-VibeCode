import CryptoJS from 'crypto-js';

const SECRET_KEY = 'your-secret-key'; // Should be stored securely

export const encryptionService = {
  encrypt: (message) => {
    try {
      return CryptoJS.AES.encrypt(message, SECRET_KEY).toString();
    } catch (error) {
      console.error('Encryption error:', error);
      return message;
    }
  },

  decrypt: (encryptedMessage) => {
    try {
      const bytes = CryptoJS.AES.decrypt(encryptedMessage, SECRET_KEY);
      return bytes.toString(CryptoJS.enc.Utf8);
    } catch (error) {
      console.error('Decryption error:', error);
      return encryptedMessage;
    }
  },

  hash: (data) => {
    return CryptoJS.SHA256(data).toString();
  },

  generateKeyPair: async () => {
    // In production, use proper RSA library
    // This is a placeholder for demonstration
    return {
      publicKey: 'public_key_placeholder',
      privateKey: 'private_key_placeholder',
    };
  },
};

export default encryptionService;

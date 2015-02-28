import base64
from Crypto.Cipher import AES

key = base64.decodebytes(b"e0bMTqmumPfFUbwzppkSbA==")
message = base64.decodebytes(b"gkw8EU4G1SDVa2/hrlv6+0ViIxB7N1i1z5MU/Hu2xkIKzH6yQzhr3vIc27IAN558kTOkacqE5DkLpRdnN1orwtIBsUHmPMkMWTOLDzVr6eRk+2Gcj2Wft7ZKrCD+FCXlKYIoa98tUD2xvoYnRwxiE2QaNywl8UtjaqpTk1+WDImBrt6uabB1WICY/qE0It3DqQ6vdUWISoTfjb+vT5h9kfZxWYUP4ykN2UtUW1biqCjj1Rb6GWGnTx6jPqF77ud0XgV1rk/Q6heSFZWV/GP23/iytDPK1HGJoJqXPx7ErQU=")

aes = AES.new(key)
decrypted = aes.decrypt(message)
print(decrypted)
print(len(decrypted))
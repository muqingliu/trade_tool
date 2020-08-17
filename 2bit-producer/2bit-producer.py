import os
import struct

def Encode(broker_str):
	ret = ""

	size = len(broker_str)
	for i in xrange(0,size):
		c = ord(struct.unpack("<c", broker_str[i:i+1])[0]) ^ 0xff
		c = chr(c)

		ret += struct.pack("<c", c)

	f = open("permission.lkc", "wb")
	if f:
		f.write(ret)
		f.close()

def Decode():
	f = open("permission.lkc", "rb")
	if f:
		encode_str = f.readline()
		size = len(encode_str)

		ret = ""
		for i in xrange(0,size):
			c = ord(struct.unpack("<c", encode_str[i:i+1])[0]) ^ 0xff
			c = chr(c)

			ret += struct.pack("<c", c)

		print ret

		f.close()

if __name__  == '__main__':
	Encode("08D2C5C1")
	Decode()
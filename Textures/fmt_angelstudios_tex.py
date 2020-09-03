# Midtown Madness / Midnight Club .TEX
# Font .tex Exporter: by Allen


# Tex Importer: by barti https://forum.xentax.com/viewtopic.php?t=12738&fbclid=IwAR3hmnYbavLryyVP9c53IGZPBHZXmhNHJs8jyGsdkabJOvtkBArjVXmCdHg#p105226
# Reference from http://mm2kiwi.apan.is-a-geek.com/index.php?title=TEX
# and http://forum.xentax.com/viewtopic.php?f=10&p=9670

from inc_noesis import *

import noesis
import rapi

def registerNoesisTypes():
	handle = noesis.register("Midtown Madness / Midnight Club", ".tex")
	noesis.setHandlerTypeCheck(handle, texCheckType)
	noesis.setHandlerLoadRGBA(handle, texLoadRGBA)
	noesis.setHandlerWriteRGBA(handle, texWriteRGBA)
	return 1

def texCheckType(data):
	return 1

def texLoadRGBA(data, texList):
	tex = AGETexture(NoeBitStream(data))
	texList.append(tex.parseTexture())
	return 1

class AGETexture:

	def __init__(self, reader):
		self.reader = reader

	def parseTexture(self):
		texWidth   = self.reader.readUShort()
		texHeight  = self.reader.readUShort()
		texType    = self.reader.readShort()
		texMips    = self.reader.readShort()
		texUnknown = self.reader.readShort()
		texFlag1   = self.reader.readUByte()
		texFlag2   = self.reader.readUByte()
		texFlag3   = self.reader.readUByte()
		texFlag4   = self.reader.readUByte()
				
		if texType == 1: # P8
			palMap = self.reader.readBytes(256*4)
			pixMap = self.reader.readBytes(texWidth * texHeight)
			pixData = rapi.imageDecodeRawPal(pixMap, palMap, texWidth, texHeight, 8, "b8g8r8p8")
		if texType == 14: # PA8
			palMap = self.reader.readBytes(256*4)
			pixMap = self.reader.readBytes(texWidth * texHeight)
			pixData = rapi.imageDecodeRawPal(pixMap, palMap, texWidth, texHeight, 8, "b8g8r8a8")
		if texType == 15: # P4_MC
			palMap = self.reader.readBytes(16*4)
			pixMap = self.reader.readBytes(int(texWidth * texHeight / 2))
			pixData = rapi.imageDecodeRawPal(pixMap, palMap, texWidth, texHeight, 4, "b8g8r8p8")
		if texType == 16: # PA4_MC
			palMap = self.reader.readBytes(16*4)
			pixMap = self.reader.readBytes(int(texWidth * texHeight / 2))
			pixData = rapi.imageDecodeRawPal(pixMap, palMap, texWidth, texHeight, 4, "b8g8r8a8")
		if texType == 17: # RGB888
			pixMap = self.reader.readBytes(texWidth * texHeight * 3)
			pixData = rapi.imageDecodeRaw(pixMap, texWidth, texHeight, "r8g8b8")
		if texType == 18: # RGBA8888
			pixMap = self.reader.readBytes(texWidth * texHeight * 4)
			pixData = rapi.imageDecodeRaw(pixMap, texWidth, texHeight, "r8g8b8a8")
		# Midnight Club 2 support (textype 26 not fully functional)
		if texType == 22: # DXT1
			pixMap = self.reader.readBytes(int(texWidth * texHeight * 4 / 8))
			pixData = rapi.imageDecodeDXT(pixMap, texWidth, texHeight, noesis.NOESISTEX_DXT1)
		if texType == 26: # DXT5
			pixMap = self.reader.readBytes(int(texWidth * texHeight * 4 / 4))
			pixData = rapi.imageDecodeDXT(pixMap, texWidth, texHeight, noesis.NOESISTEX_DXT5)
			
		#pixData = rapi.imageFlipRGBA32(pixData, texWidth, texHeight, 0, 1)
		return NoeTexture("tex", texWidth, texHeight, pixData, noesis.NOESISTEX_RGBA32)
	
def texWriteRGBA(data, width, height, bs):
        bs.writeShort(width)
        bs.writeShort(height)
        bs.writeShort(16)
        bs.writeShort(1)
        bs.writeShort(0)
        bs.writeByte(1)
        bs.writeByte(0)
        bs.writeByte(1)        
        bs.writeByte(0)       
        imgPix = rapi.imageResample(data, width, height, width, height)
        imgPal = rapi.imageGetPalette(imgPix, width, height, 16, 0, 1)
        idxPix = rapi.imageApplyPalette(imgPix, width, height, imgPal, 16)

        #bgra 32bpp palette
        for i in range(0,16):
                bs.writeUByte(imgPal[i*4+2])
                bs.writeUByte(imgPal[i*4+1])
                bs.writeUByte(imgPal[i*4+0])
                bs.writeUByte(imgPal[i*4+3])
        #4bpp indexed palette image       
        for i in range(width*height//2):
                idx2 = idxPix[i*2+0]
                idx1 = idxPix[i*2+1]
                idx = ((idx1 << 4) | idx2) & 0xff
                bs.writeUByte(idx)
        return 1

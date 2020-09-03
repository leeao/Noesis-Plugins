#by Allen

from inc_noesis import *

import noesis
import rapi
import math

alphaEncodingTable = (
        0,   1,   1,   2,   2,   3,   3,   4,   4,   5,   5,   6,   6,   7,   7,   8,
        8,   9,   9,   10,  10,  11,  11,  12,  12,  13,  13,  14,  14,  15,  15,  16,
        16,  17,  17,  18,  18,  19,  19,  20,  20,  21,  21,  22,  22,  23,  23,  24,
        24,  25,  25,  26,  26,  27,  27,  28,  28,  29,  29,  30,  30,  31,  31,  32,
        32,  33,  33,  34,  34,  35,  35,  36,  36,  37,  37,  38,  38,  39,  39,  40,
        40,  41,  41,  42,  42,  43,  43,  44,  44,  45,  45,  46,  46,  47,  47,  48,
        48,  49,  49,  50,  50,  51,  51,  52,  52,	 53,  53,  54,  54,  55,  55,  56,
        56,  57,  57,  58,  58,  59,  59,  60,  60,  61,  61,  62,  62,  63,  63,  64,
        64,  65,  65,  66,  66,  67,  67,  68,  68,  69,  69,  70,  70,  71,  71,  72,
        72,  73,  73,  74,  74,  75,  75,  76,  76,  77,  77,  78,  78,  79,  79,  80,
        80,  81,  81,  82,  82,  83,  83,  84,  84,  85,  85,  86,  86,  87,  87,  88,
        88,  89,  89,  90,  90,  91,  91,  92,  92,  93,  93,  94,  94,  95,  95,  96,
        96,  97,  97,  98,  98,  99,  99,  100, 100, 101, 101, 102, 102, 103, 103, 104,
        104, 105, 105, 106, 106, 107, 107, 108, 108, 109, 109, 110, 110, 111, 111, 112,
        112, 113, 113, 114, 114, 115, 115, 116, 116, 117, 117, 118, 118, 119, 119, 120,
        120, 121, 121, 122, 122, 123, 123, 124, 124, 125, 125, 126, 126, 127, 127, 128
    )

alphaDecodingTable = (

        0,   2,   4,   6,   8,   10,  12,  14,  16,  18,  20,  22,  24,  26,  28,  30,
        32,  34,  36,  38,  40,  42,  44,  46,  48,  50,  52,  54,  56,  58,  60,  62,
        64,  66,  68,  70,  72,  74,  76,  78,  80,  82,  84,  86,  88,  90,  92,  94,
        96,  98,  100, 102, 104, 106, 108, 110, 112, 114, 116, 118, 120, 122, 124, 126,
        128, 129, 131, 133, 135, 137, 139, 141, 143, 145, 147, 149, 151, 153, 155, 157,
        159, 161, 163, 165, 167, 169, 171, 173, 175, 177, 179, 181, 183, 185, 187, 189,
        191, 193, 195, 197, 199, 201, 203, 205, 207, 209, 211, 213, 215, 217, 219, 221,
        223, 225, 227, 229, 231, 233, 235, 237, 239, 241, 243, 245, 247, 249, 251, 253,
        255

    )

def registerNoesisTypes():
	handle = noesis.register("Onimusha 3 PS2 Textures ", ".oim")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
	noesis.setHandlerWriteRGBA(handle, noepyWriteRGBA)

	noesis.addOption(handle, "-4bpp", "convert to 4bpp 16 colors image. defalut is 8bpp 256 colors image.", 0)
	return 1

def noepyCheckType(data):
        bs = NoeBitStream(data)
        magic = noeStrFromBytes(bs.readBytes(4))
        if magic != "OIM3":
            return 0
        return 1

def noepyLoadRGBA(data, texList):

        bs = NoeBitStream(data)
        magic = noeStrFromBytes(bs.readBytes(4))
        fileSize = bs.readInt()
        bs.seek(3,1)
        numTex = bs.readUByte()
        numPal = bs.readUByte()
        bs.seek(3,1)
        
        for i in range(numTex):
                
                pixelOffset = bs.readInt()
                pixelSize = bs.readInt()
                width = 1 << bs.readByte()
                height = 1 << bs.readByte()
                texFormat = bs.readByte()
                null = bs.readByte()
                texID = bs.readInt()
                nextOfs = bs.tell()
                
                palOfs = 16 + (numTex * 16) + (i * 16)
                bs.seek(palOfs)
                palOffset = bs.readInt()
                palSize = bs.readInt()
                palWidth = 1 << bs.readByte()
                palHeight = 1 << bs.readByte()
                palFormat = bs.readByte()
                null = bs.readByte()
                zero = bs.readInt()

                bs.seek(pixelOffset)
                pixels = bs.readBytes(pixelSize)

                bs.seek(palOffset)
                palette = bs.readBytes(palSize)
                newPal = bytearray(palSize)
                for p in range(palSize // 4):
                    newPal[p*4] = palette[p*4]
                    newPal[p*4+1] = palette[p*4+1]
                    newPal[p*4+2] = palette[p*4+2]
                    newPal[p*4+3] = alphaDecodingTable[palette[p*4+3]]
                palette = newPal

                if texFormat == 0x13:
                        textureData = rapi.imageDecodeRawPal(pixels,palette,width,height,8,"r8 g8 b8 a8",noesis.DECODEFLAG_PS2SHIFT)
                        texList.append(NoeTexture(rapi.getInputName()[-4:]+str(texID), width, height, textureData, noesis.NOESISTEX_RGBA32))
                elif texFormat == 0x14:
                        textureData = rapi.imageDecodeRawPal(pixels,palette,width,height,4,"r8 g8 b8 a8")
                        texList.append(NoeTexture(rapi.getInputName()[-4:]+str(texID), width, height, textureData, noesis.NOESISTEX_RGBA32))

                bs.seek(nextOfs)
        return 1

#judge if it is a power of 2
def judge(num):
            num = int(num)
            return True if num == 0 or num & (num - 1) == 0 else False

def noepyWriteRGBA(data, width, height, bs):
        if (judge(width) == False) or (judge(height) == False):
                print("Error: width or height not power of 2.")
                return 0
        logWidth = int(math.log(width,2))
        logHeight =  int(math.log(height,2))
        bs.writeString("OIM3",0)
        bs.writeInt(0);
        bs.writeUInt(0x1000000)
        bs.writeUInt(1)

        if noesis.optWasInvoked("-4bpp"):
                imgPal = rapi.imageGetPalette(data, width, height, 16, 0, 1)
                idxPix = rapi.imageApplyPalette(data, width, height, imgPal, 16)
                texFormat = 0x14
                logPalWidth = 4
                palSize = 64
                pixelSize = len(idxPix) // 2
        else:
                imgPal = rapi.imageGetPalette(data, width, height, 256, 0, 1)
                idxPix = rapi.imageApplyPalette(data, width, height, imgPal, 256)
                palSize = 1024
                pixelSize = len(idxPix)
                texFormat = 0x13
                logPalWidth = 8                
                
        bs.writeInt(0x30)               #pixel offset
        bs.writeInt(pixelSize)          #pixel size
        bs.writeByte(logWidth)
        bs.writeByte(logHeight)
        bs.writeByte(texFormat)
        bs.writeByte(0)
        bs.writeInt(0)                  #texID

        bs.writeInt(0x30+pixelSize)
        bs.writeInt(palSize)
        bs.writeByte(logPalWidth)       #pal width
        bs.writeByte(1)                 #pal height
        bs.writeByte(0)                 #pal format
        bs.writeByte(0) 
        bs.writeInt(0)
        if texFormat == 0x14:
                #4bpp indexed palette image       
                for i in range(width*height//2):
                        idx2 = idxPix[i*2+0]
                        idx1 = idxPix[i*2+1]
                        idx = ((idx1 << 4) | idx2) & 0xff
                        bs.writeUByte(idx)
                #rgba 32bpp palette                
                for i in range(0,16):
                        bs.writeUByte(imgPal[i*4+0])
                        bs.writeUByte(imgPal[i*4+1])
                        bs.writeUByte(imgPal[i*4+2])
                        alpha = alphaEncodingTable[imgPal[i*4+3]]
                        bs.writeUByte(alpha)
                        
        elif texFormat == 0x13:
                bs.writeBytes(idxPix)
                
                for i in range(8):                 #do this 8 times
                        for j in range(8):              #write 1st 32 byte block of palette
                                bs.writeUByte(imgPal[(i*128+j*4)+0])
                                bs.writeUByte(imgPal[(i*128+j*4)+1])
                                bs.writeUByte(imgPal[(i*128+j*4)+2])
                                alpha = alphaEncodingTable[imgPal[(i*128+j*4)+3]]
                                bs.writeUByte(alpha)                                
                        for j in range(8):              #write 3rd 32 byte block of palette
                                bs.writeUByte(imgPal[(i*128+64+j*4)+0])
                                bs.writeUByte(imgPal[(i*128+64+j*4)+1])
                                bs.writeUByte(imgPal[(i*128+64+j*4)+2])
                                alpha = alphaEncodingTable[imgPal[(i*128+64+j*4)+3]]
                                bs.writeUByte(alpha)                                        
                        for j in range(8):              #write 2nd 32 byte block of palette
                                bs.writeUByte(imgPal[(i*128+32+j*4)+0])
                                bs.writeUByte(imgPal[(i*128+32+j*4)+1])
                                bs.writeUByte(imgPal[(i*128+32+j*4)+2])
                                alpha = alphaEncodingTable[imgPal[(i*128+32+j*4)+3]]
                                bs.writeUByte(alpha)                                        
                        for j in range(8):              #write 4th 32 byte block of palette
                                bs.writeUByte(imgPal[(i*128+96+j*4)+0])
                                bs.writeUByte(imgPal[(i*128+96+j*4)+1])
                                bs.writeUByte(imgPal[(i*128+96+j*4)+2])
                                alpha = alphaEncodingTable[imgPal[(i*128+96+j*4)+3]]
                                bs.writeUByte(alpha)
                
        fileSize = bs.tell()
        bs.seek(4)
        bs.writeUInt(fileSize)
                
        return 1

#by Allen
from inc_noesis import *
def registerNoesisTypes():
    handle = noesis.register("Road Trip Adventure PS2 textures", ".e3d;.dat;.gsl;.bin;")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

pixelFlag = (0x1012,0x1040,0x1087)
palFlag = (0x10ff,0x1040)

def noepyCheckType(data):
    bs = NoeBitStream(data)
    bs.seek(2)
    idstring = bs.readShort()
    if idstring not in pixelFlag:
	    return 0
    return 1


def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    

    index = 0
    while bs.tell() < bs.getSize():
        chunkFlag = bs.readUInt() >> 16
        bs.seek(-4,1)
        if chunkFlag not in pixelFlag and chunkFlag not in palFlag:
            bs.seek(bs.getSize())
            break
        
        tex = Texture(bs)
        tex.readTex()
        if chunkFlag in pixelFlag:
            
            texPal = Texture(bs,False)
            texPal.readTex()
            texName = rapi.getExtensionlessName(rapi.getInputName())+"_"+str(index)
            
            if texPal.chunkSize == 128:            
                textureData = rapi.imageDecodeRawPal(tex.pixels,texPal.pals,tex.width,tex.height,4,"r8g8b8a8")
                texList.append(NoeTexture(texName, tex.width, tex.height, textureData, noesis.NOESISTEX_RGBA32))
            elif texPal.chunkSize == 1024:
                textureData = rapi.imageDecodeRawPal(tex.pixels,texPal.pals,tex.width,tex.height,8,"r8g8b8a8",noesis.DECODEFLAG_PS2SHIFT)
                texList.append(NoeTexture(texName, tex.width, tex.height, textureData, noesis.NOESISTEX_RGBA32))
            elif texPal.chunkSize == 512:
                textureData = rapi.imageDecodeRawPal(tex.pixels,texPal.pals,tex.width,tex.height,4,"r5g5b5p1",noesis.DECODEFLAG_PS2SHIFT)
                texList.append(NoeTexture(texName, tex.width, tex.height, textureData, noesis.NOESISTEX_RGBA32))
            
            index += 1
    return 1

class Texture(object):
    def __init__(self,bs,readPixel=True):
        self.bs = bs
        self.dataSize = 0
        self.chunkSize = 0
        self.chunkFlag = 0
        self.width = 0
        self.height = 0
        self.pixels = bytes()
        self.pals = bytes()
        self.colors = 0
        self.readPixel = readPixel
    def readTex(self):
        baseOfs = self.bs.tell()
        dataSizeFlag = self.bs.readShort()
        self.dataSize = (dataSizeFlag & 0xFFF0) * 16
        self.chunkFlag = self.bs.readShort()
        self.bs.seek(0x3c,1)
        self.width = self.bs.readShort() & 0xFFF
        unk = self.bs.readShort()
        self.height = self.bs.readShort() & 0xFFF
        unk2 = self.bs.readShort()
        self.bs.seek(24,1)
        self.chunkSize = self.bs.readShort() * 16
        self.bs.seek(14,1)
        if self.readPixel:
            self.pixels = self.bs.readBytes(self.chunkSize)
        else:
            if self.chunkSize == 128:
                self.colors = 16
                for i in range(8):
                    self.pals += rgba32(self.bs.readUInt())
                self.bs.seek(32,1)
                for i in range(8):
                    self.pals += rgba32(self.bs.readUInt())
                self.bs.seek(32,1)
                
            elif self.chunkSize == 1024:
                self.colors = 256
                for i in range(256):
                    self.pals += rgba32(self.bs.readUInt())
                    
            elif self.dataSize == 512:
                self.colors = 256
                self.pals = self.bs.readBytes(self.chunkSize)
               
def rgba32(rawPixel):
    t = bytearray(4)
    t[0] = rawPixel & 0xFF
    t[1] = (rawPixel >> 8) & 0xFF
    t[2] = (rawPixel >> 16)  & 0xFF
    t[3] = min(((rawPixel >> 24) & 0xFF)*2, 255)
    return t


from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Road Trip Adventure PS2 textrues", ".dat")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):
    bs = NoeBitStream(data)
    bs.seek(2)
    idstring = bs.readShort()
    if idstring!=0x1012:
	    return 0
    return 1

pixelFlag = 0x1012
palFlag = 0x10FF

def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    
    chunkFlag = pixelFlag

    index = 1
    while (chunkFlag == pixelFlag) or (chunkFlag == palFlag):
        chunkFlag = bs.readUInt() >> 16
        bs.seek(-4,1)
        if chunkFlag != pixelFlag and chunkFlag != palFlag:
            break
        
        tex = Texture(bs)
        tex.readTex()
        
        texPal = Texture(bs)
        texPal.readTex()
        texName = rapi.getExtensionlessName(rapi.getInputName())+"_"+str(index)
        if texPal.colors == 16:            
            textureData = rapi.imageDecodeRawPal(tex.pixels,texPal.pals,tex.width,tex.height,4,"r8g8b8a8")
            texList.append(NoeTexture(texName, tex.width, tex.height, textureData, noesis.NOESISTEX_RGBA32))
        elif texPal.colors == 256:
            textureData = rapi.imageDecodeRawPal(tex.pixels,texPal.pals,tex.width,tex.height,8,"r8g8b8a8",noesis.DECODEFLAG_PS2SHIFT)
            texList.append(NoeTexture(texName, tex.width, tex.height, textureData, noesis.NOESISTEX_RGBA32))
        index += 1
    return 1

class Texture(object):
    def __init__(self,bs):
        self.bs = bs
        self.dataSize = 0
        self.chunkFlag = 0
        self.width = 0
        self.height = 0
        self.pixels = bytes()
        self.pals = bytes()
        self.colors = 0
    def readTex(self):
        baseOfs = self.bs.tell()
        self.dataSize = (self.bs.readShort() & 0xFFF0) * 16
        self.chunkFlag = self.bs.readShort()
        self.bs.seek(0x3c,1)
        self.width = self.bs.readShort() & 0xFFF
        unk = self.bs.readShort()
        self.height = self.bs.readShort() & 0xFFF
        unk2 = self.bs.readShort()
        self.bs.seek(40,1)
        if self.chunkFlag == pixelFlag:
            self.pixels = self.bs.readBytes(self.dataSize)
        elif self.chunkFlag == palFlag:
            if (self.width * self.height) == 256:
                self.colors = 256
                for i in range(256):
                    self.pals += rgba32(self.bs.readUInt())
            elif (self.width * self.height) == 32:
                self.colors = 16
                
                for i in range(8):
                    self.pals += rgba32(self.bs.readUInt())
                self.bs.seek(32,1)
                for i in range(8):
                    self.pals += rgba32(self.bs.readUInt())
                self.bs.seek(32,1)

                
def rgba32(rawPixel):
    t = bytearray(4)
    t[0] = rawPixel & 0xFF
    t[1] = (rawPixel >> 8) & 0xFF
    t[2] = (rawPixel >> 16)  & 0xFF
    t[3] = min(((rawPixel >> 24) & 0xFF)*2, 255)
    return t

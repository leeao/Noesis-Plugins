#by Allen
from inc_noesis import *
def registerNoesisTypes():
    handle = noesis.register("Naruto Uzumaki Chronicles 2 PS2 Font textures", ".texture")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):
    bs = NoeBitStream(data)
    return 1

def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)

    numTex = bs.readInt()
    numTexChunk = bs.readInt()
    bs.seek(8,1)
    bs.seek(80*numTex,1)
    bs.seek(20*numTex,1)
    texPalette = bytearray(64) #4bpp font
    
    for i in range(numTex):
        nextOfs = bs.tell() + 16
        tex = Texture(bs)
        tex.readTex()
        if i == 0:
            bs.seek(nextOfs)
            texPal = Texture(bs,False)
            texPal.readTex()
            texPalette[0:64] = texPal.pals[0:64]
            nextOfs += 16
        
        texName = "font_"+str(i)
        width = tex.width * 2
        height = tex.height * 4

        pixel = rapi.imageUntwiddlePS2(tex.pixels,width,height,4)
        textureData = rapi.imageDecodeRawPal(pixel,texPalette,width,height,4,"r8g8b8a8"  )
        texList.append(NoeTexture(texName, width, height, textureData, noesis.NOESISTEX_RGBA32))

        bs.seek(nextOfs)
    return 1

class Texture(object):
    def __init__(self,bs,readPixel=True):
        self.bs = bs
        self.chunkSize = 0
        self.width = 0
        self.height = 0
        self.pixels = bytes()
        self.pals = bytes()
        self.colors = 0
        self.readPixel = readPixel
    def readTex(self):
        baseOfs = self.bs.tell()
        unk = self.bs.readInt()
        dataOfs = baseOfs + self.bs.readUInt()
        self.width = self.bs.readShort()
        self.height = self.bs.readShort()
        unk2 = self.bs.readShort()
        unk3 = self.bs.readByte()
        unk4 = self.bs.readByte()

        self.chunkSize = self.width * self.height * 4
        self.bs.seek(dataOfs)
        
        if self.readPixel:
            self.pixels = self.bs.readBytes(self.chunkSize)
        else:    
            if self.chunkSize == 1024:
                self.colors = 256
                for i in range(256):
                    self.pals += rgba32(self.bs.readUInt())
            elif self.chunkSize == 64:
                self.colors = 16
                for i in range(16):
                    self.pals += rgba32(self.bs.readUInt())
            else:
                print("unknown format. size:",self.chunkSize)                
def rgba32(rawPixel):
    t = bytearray(4)
    t[0] = rawPixel & 0xFF
    t[1] = (rawPixel >> 8) & 0xFF
    t[2] = (rawPixel >> 16)  & 0xFF
    t[3] = min(((rawPixel >> 24) & 0xFF)*2, 255)
    return t


from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Twisted Metal Black PS2", ".tex")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):
    return 1


def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    numTextures = 0
    numSizeType = bs.readInt()
    texOfs = bs.readInt() * 16
    for i in range(numSizeType):
        typeNumTex = bs.readUByte()
        bs.readByte()
        bs.readShort()
        typeSize = bs.readInt() #pixel data size
        numTextures += typeNumTex
    #print(numTextures)
    bs.seek(texOfs)
    #for i in range(numTextures):
    while(bs.tell()<bs.getSize()):
        tex = Texture(bs)
        tex.read()
        if tex.chunkFlag == 8:
            if tex.isPALImage:
                texPal = Texture(bs)
                texPal.read()
                if texPal.chunkFlag == 0x88:
                    if texPal.colors == 256:
                        #print("PAL8")
                        palette = bytes()
                        for p in range(256):
                            palette += rgba32(texPal.palette[p])                           
                        pixel = rapi.imageUntwiddlePS2(tex.pixel, tex.width, tex.height, 8)
                        textureData = rapi.imageDecodeRawPal(pixel,palette,tex.width,tex.height,8,"r8g8b8a8", noesis.DECODEFLAG_PS2SHIFT)
                        texList.append(NoeTexture(rapi.getInputName()+str(i), tex.width, tex.height, textureData, noesis.NOESISTEX_RGBA32))
                    elif texPal.colors == 16:
                        #print("PAL4") 
                        palette = bytes()
                        for p in range(16):
                            palette += rgba32(texPal.palette[p])                
                        
                        textureData = rapi.imageDecodeRawPal(tex.pixel,palette,tex.width,tex.height,4,"r8g8b8a8")
                        texList.append(NoeTexture(rapi.getInputName()+str(i), tex.width, tex.height, textureData, noesis.NOESISTEX_RGBA32))
            elif tex.bpp == 32 :
                width = tex.width // 2
                height = tex.height // 2
                pixel = parseRgba32(tex.pixel,width,height)
                textureData = rapi.imageDecodeRaw(pixel,width,height,"r8g8b8a8")
                texList.append(NoeTexture(rapi.getInputName()+str(i), width,height, textureData, noesis.NOESISTEX_RGBA32))
        elif tex.chunkFlag & 0x20 == 0x20:
                textureData = rapi.imageDecodeRaw(tex.pixel,tex.width,tex.height,"a8")
                texList.append(NoeTexture(rapi.getInputName()+str(i), tex.width,tex.height, textureData, noesis.NOESISTEX_RGBA32))
        elif tex.chunkFlag & 0x40 == 0x40:
                textureData = rapi.imageDecodeRaw(tex.pixel,tex.width,tex.height,"a4")
                texList.append(NoeTexture(rapi.getInputName()+str(i), tex.width,tex.height, textureData, noesis.NOESISTEX_RGBA32))
    return 1


class Texture(object):

    def __init__(self, bs):
        self.bs = bs
        self.bpp = 0
        self.width = 0
        self.height= 0
        self.colors = 0
        self.chunkFlag = 0
        self.pixel = bytes()
        self.palette = bytes()
        self.isPALImage = True
    def read(self):
        
        rest = self.bs.readUByte()        
        kilos = self.bs.readUShort()
        unk = self.bs.readByte()
        unk2 = self.bs.readShort()
        unk3 = self.bs.readShort()
        unk4 = self.bs.readInt()
        palFlag = self.bs.readByte()
        sizeFlag = self.bs.readByte()
        chunkFlag = self.bs.readUByte()
        unkFlag = self.bs.readByte()
        self.chunkFlag = chunkFlag
        self.bs.seek(112,1)

        self.height =  2 << ((sizeFlag & 0xf0) >> 4)
        self.width = 2 << (sizeFlag & 0xf)
        if chunkFlag == 0x8:      
            if self.width > 256:
                self.isPALImage = False
                self.bpp = 32
        if chunkFlag & 0x20 == 0x20 or chunkFlag & 0x40 == 0x40 :
            self.isPALImage = False
            self.height =  1 << ((sizeFlag & 0xf0) >> 4)
            self.width = 1 << (sizeFlag & 0xf)
        chunkSize = kilos * 1024 + rest * 4
        dataSize = 0
        if chunkSize > 0:
            dataSize = chunkSize - 128
        if chunkSize == 0:
            dataSize = self.bs.getSize() - self.bs.tell()
        if chunkFlag == 0x20:
            self.bpp = 8
        elif chunkFlag == 0x40:
            self.bpp = 4
        
        if chunkFlag == 0x88:
            if dataSize == 128:
                self.colors = 16
                self.bpp = 4
            elif dataSize == 1024:
                self.colors = 256
                self.bpp = 8
                
        width = self.width
        height = self.height            
        if chunkFlag == 0x88:
            #print("get palette buffer")
            colors = []
            for i in range(self.colors):
                colors.append(self.bs.readUInt())
            self.palette = colors
            if self.colors == 16:
                self.bs.seek(64,1)
        else:
            #print("get pixel buffer")
            self.pixel = self.bs.readBytes(dataSize)
            
        #print("dataSize:",dataSize)

def rgba32(rawPixel):
    t = bytearray(4)
    t[0] = rawPixel & 0xFF
    t[1] = (rawPixel >> 8) & 0xFF
    t[2] = (rawPixel >> 16)  & 0xFF
    t[3] = min(((rawPixel >> 24) & 0xFF)*2, 255)
    return t

def parseRgba32(buf,width,height):
    ms = NoeBitStream(buf)
    outPixel = bytes()
    for i in range(width*height):
        pixel = ms.readUInt()
        outPixel += bytes(rgba32(pixel))
    return outPixel


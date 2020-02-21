#by Allen

#8bpp unswizzle code http://gtamodding.ru/wiki/TIM2
#palette unswizzle code https://github.com/Sor3nt/manhunt-toolkit/blob/master/App/Service/Archive/Textures/Playstation.php

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Twisted Metal Black PS2", ".tex")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):
    bs = NoeBitStream(data)
    bs.seek(4)
    ids = bs.readInt()
    if ids != 0xf :
	    return 0
    return 1


def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    numTextures = 0
    numSizeType = bs.readInt()
    ids = bs.readInt()
    for i in range(numSizeType):
        typeNumTex = bs.readUByte()
        bs.readByte()
        bs.readShort()
        typeSize = bs.readInt() #pixel data size
        numTextures += typeNumTex
    
    bs.seek(0xF0)
    for i in range(numTextures):
        
        tex = Texture(bs)
        tex.read()
        nextOfs = bs.tell()
        
        texPal = Texture(bs)
        texPal.read()
        if  texPal.chunkFlag == 8: #not palette, so the tex is 32bpp
            bs.seek(nextOfs) # back to next
            width = tex.width//2
            height = tex.height//2
            pixel = parseRgba32(tex.pixel,width,height)
            textureData = rapi.imageDecodeRaw(pixel,width,height,"r8g8b8a8")
            texList.append(NoeTexture(rapi.getInputName()+str(i), width,height, textureData, noesis.NOESISTEX_RGBA32))
            
        elif texPal.chunkFlag == 0x88:
            if texPal.colors == 256:
                texPal.palette = unswizzlePalette(texPal.palette,texPal.colors)
                pixel = unswizzle8(tex.pixel,tex.width,tex.height)
                textureData = rapi.imageDecodeRawPal(pixel,texPal.palette,tex.width,tex.height,8,"r8g8b8a8")
                texList.append(NoeTexture(rapi.getInputName()+str(i), tex.width, tex.height, textureData, noesis.NOESISTEX_RGBA32))
            elif texPal.colors == 16:
                palette = bytes()
                for i in range(16):
                    palette += rgba32(texPal.palette[i])                
                
                pixel = convert4to8(tex.pixel,tex.width,tex.height)
                textureData = rapi.imageDecodeRawPal(pixel,palette,tex.width,tex.height,8,"r8g8b8a8")
                texList.append(NoeTexture(rapi.getInputName()+str(i), tex.width, tex.height, textureData, noesis.NOESISTEX_RGBA32)) 
    return 1

def unswizzle8(buf,width,height):
    out = bytearray(width*height)
    for y in range(height):
        for x in range(width):
            block_location = (y & (~0xf)) * width + (x & (~0xf)) * 2
            swap_selector = (((y + 2) >> 2) & 0x1) * 4
            posY = (((y & (~3)) >> 1) + (y & 1)) & 0x7
            column_location = posY * width * 2 + ((x + swap_selector) & 0x7) * 4
            byte_num = ((y >> 1) & 1) + ((x >> 2) & 2)
            swizzleid = block_location + column_location + byte_num
            out[y * width + x] = buf[swizzleid]
    return out
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
    def read(self):
        #print(self.bs.tell())
        rest = self.bs.readByte()        
        kilos = self.bs.readShort()
        unk = self.bs.readByte()
        unk2 = self.bs.readShort()
        unk3 = self.bs.readShort()
        unk4 = self.bs.readInt()
        palFlag = self.bs.readByte()
        sizeFlag = self.bs.readByte()
        chunkFlag = self.bs.readShort()
        self.chunkFlag = chunkFlag
        self.bs.seek(112,1)
        self.width =  2 << ((sizeFlag & 0xf0) >> 4)
        self.height = 2 << (sizeFlag & 0xf)
        dataSize = self.width * self.height
        if dataSize == 64:
            self.colors = 16
            self.bpp = 4
        elif dataSize == 1024:
            self.colors = 256
            self.bpp = 8
        else:
            self.bpp = 8
        width = self.width
        height = self.height            
        if chunkFlag == 0x88:
            colors = []
            for i in range(self.colors):
                colors.append(self.bs.readUInt())
            self.palette = colors
            if self.colors < 256:
                self.bs.seek(64,1)
        elif chunkFlag == 8:
            self.pixel = self.bs.readBytes(width*height)
def convert4to8(buf,width,height):
    out = bytearray(width*height)
    for i in range(width*height//2):
        index = buf[i]
        out[i*2] = (index >> 4) & 0xf
        out[i*2+1] = index & 0xf
    return out

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

def unswizzlePalette(colorMap,colors):
    numBlocks = colors//8
    palBlock=[]
    for i in range(0,numBlocks):
        subBlock=[]                
        for j in range(8):
            subBlock.append(colorMap[i*8+j])
        palBlock.append(subBlock)
    newPalette = []
    current = 0
    swapCount = 2
    while current < numBlocks :
        block = palBlock[current]
        if current == 0:
            newPalette.append(block)
            current+=1
            swapCount = 2
            continue
        if swapCount == 2:
            newPalette.append(palBlock[current+1])
            newPalette.append(palBlock[current])
            current+=1
            swapCount = 0
        else:
            newPalette.append(block)
            swapCount+=1
        current+=1
    finalPal = []
    for i in range(0,numBlocks):
        subBlock = newPalette[i]
        for j in range(8):
            finalPal.append(subBlock[j])
    palette =bytes()
    for i in range(colors):
        palette += rgba32(finalPal[i])
    return palette

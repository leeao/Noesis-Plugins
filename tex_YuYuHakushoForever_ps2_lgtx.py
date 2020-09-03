from inc_noesis import *
def registerNoesisTypes():
    handle = noesis.register("Yu Yu Hakusho Forever PS2 Texture LGTX", ".lgtx")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):
    bs = NoeBitStream(data)
    idstring = bs.readInt()
    if idstring!=0x5854474C: #"LGTX"
	    return 0
    return 1

def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    bs.seek(8)
    texName = bs.readString()
    bs.seek(0x2c)
    dataSize = bs.readInt()
    bs.seek(0x3c)
    width = bs.readShort()
    height = bs.readShort()
    bs.seek(0x7c)
    pixelOffset = bs.readInt()
    bs.seek(0x15C)
    paletteOffset = bs.readInt()

    bs.seek(pixelOffset+0x50)
    pixel = bs.readBytes(width*height)
    bs.seek(paletteOffset+0x20)
    palWidth = bs.readInt()
    palHeight = bs.readInt()
    
    bs.seek(0x28,1)
    palFormat = palWidth * palHeight
    if palFormat == 256:
        palette = bytes()
        for i in range(256):
            palette += rgba32(bs.readUInt())            
        pixel = rapi.imageUntwiddlePS2(pixel,width,height,8)
        textureData = rapi.imageDecodeRawPal(pixel,palette,width,height,8,"r8g8b8a8",noesis.DECODEFLAG_PS2SHIFT)
        texList.append(NoeTexture(texName, width, height, textureData, noesis.NOESISTEX_RGBA32))        
    else:
        print("unk format can't support.")
    return 1

                
def rgba32(rawPixel):
    t = bytearray(4)
    t[0] = rawPixel & 0xFF
    t[1] = (rawPixel >> 8) & 0xFF
    t[2] = (rawPixel >> 16)  & 0xFF
    t[3] = min(((rawPixel >> 24) & 0xFF)*2, 255)
    return t

#by Allen
#wiki http://www.gtamodding.ru/wiki/TIM2

from inc_noesis import *
def registerNoesisTypes():
    handle = noesis.register("kater thps hawk .tex.ps2 textrues", ".ps2")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):
    if len(data) < 8:
	    return 0
    return 1
decodeTexSize=(1,2,4,8,16,32,64,128,256,512,1024,2048)

def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    bs.seek(0x8)
    numTextures = bs.readInt()
    bs.seek(0x1C)
    for i in range(numTextures):
        bs.readInt()
        bs.readInt()    
        width = decodeTexSize[bs.readInt()]
        height = decodeTexSize[bs.readInt()]
        unk1=bs.readInt()
        unk2=bs.readInt()
        unk3=bs.readInt()
        curOfs = bs.tell()
        if curOfs % 16:
            palLen = 16 - (curOfs % 16)
            bs.seek(palLen,1)
        palette = bs.readBytes(512)
        pixel = bs.readBytes(width*height)
        pixel = unswizzle8(pixel,width,height)
        textureData = rapi.imageDecodeRawPal(pixel,palette,width,height,8,"r5g5b5a1")
        texList.append(NoeTexture(rapi.getInputName(), width, height, textureData, noesis.NOESISTEX_RGBA32))   
    return 1

def unswizzle8(buf,width,height):
    swizzled = bytearray(width*height)
    swizzled[0:(width*height)] = buf[0:(width*height)]
    out = bytearray(width*height)
    for y in range(height):
        for x in range(width):
            block_location = (y & (~0xf)) * width + (x & (~0xf)) * 2
            swap_selector = (((y + 2) >> 2) & 0x1) * 4
            posY = (((y & (~3)) >> 1) + (y & 1)) & 0x7
            column_location = posY * width * 2 + ((x + swap_selector) & 0x7) * 4
            byte_num = ((y >> 1) & 1) + ((x >> 2) & 2)# 0,1,2,3
            out[(y * width) + x] = swizzled[block_location + column_location + byte_num]
    return out

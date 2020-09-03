#by Allen

from inc_noesis import *
def registerNoesisTypes():
    handle = noesis.register("Patapon 2 gxt font texture PSP", ".gxt")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):
    bs = NoeBitStream(data)
    idstring = bs.readInt()
    if idstring != 0x2e475858:
	    return 0
    return 1

def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    
    bs.seek(0x100C0)
    palette1 = bs.readBytes(16)
    bs.seek(0x10140)
    palette2 = bs.readBytes(16)
    bs.seek(0x101C0)
    palette3 = bs.readBytes(16)

    bs.seek(0x80)
    width = 256
    height = 256
    pixelsA = bytearray(width*height)
    pixelsB = bytearray(width*height)
    pixelsC = bytearray(width*height)
    pixelsD = bytearray(width*height)

    for i in range(width*height):
        byteArray = decode2BPP(bs.readUByte())
        pixelsA[i] = byteArray[0]
        pixelsB[i] = byteArray[1]
        pixelsC[i] = byteArray[2]
        #pixelsD[i] = byteArray[3]
    palFormat = "r8g8b8a8"
    textureData = rapi.imageDecodeRawPal(pixelsA,palette1,width,height,8,palFormat)
    textureData2 = rapi.imageDecodeRawPal(pixelsB,palette2,width,height,8,palFormat)
    textureData3 = rapi.imageDecodeRawPal(pixelsC,palette3,width,height,8,palFormat)
    #textureData4 = rapi.imageDecodeRawPal(pixelsD,palette1,width,height,8,palFormat)
    
    #display
    texList.append(NoeTexture(rapi.getInputName(), width, height, textureData, noesis.NOESISTEX_RGBA32))
    texList.append(NoeTexture(rapi.getInputName(), width, height, textureData2, noesis.NOESISTEX_RGBA32))
    texList.append(NoeTexture(rapi.getInputName(), width, height, textureData3, noesis.NOESISTEX_RGBA32))  
    #texList.append(NoeTexture(rapi.getInputName(), width, height, textureData4, noesis.NOESISTEX_RGBA32)) 
    return 1

def decode2BPP(byte_index):
    t = bytearray(4)
    t[3] = (byte_index >> 6) & 0x3
    t[2] = (byte_index >> 4) & 0x3
    t[1] = (byte_index >> 2) & 0x3
    t[0] = byte_index & 0x3
    return t


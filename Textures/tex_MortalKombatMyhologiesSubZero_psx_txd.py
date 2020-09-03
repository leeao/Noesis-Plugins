from inc_noesis import *


def registerNoesisTypes():
    handle = noesis.register("Mortal Kombat Myhologies Sub Zero PSX Texture txd", ".txd")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):

    return 1

def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    numTextures = bs.readInt()
    numPalettes = bs.readInt()

    
    pixels = []
    pals = []
    texInfoList = []
    texPalInfoList =[]
    for i in range(numTextures):
        unk1 = bs.readUByte()
        unk2 = bs.readUByte()
        unk3 = bs.readUByte()
        texType = bs.readUByte()
        width = bs.readUShort() & 0x1ff
        height = bs.readUShort() & 0x1ff
        if width > 256:
            width = width & 0xff
        if height > 256:
            height = height & 0xff
        pixelDataSize = width * height
        if (texType==0x80):
            pixelDataSize //= 2
        texID = bs.readUByte()
        unkID = bs.readUByte()
        unkID2 = bs.readShort()
        pixels.append(bs.readBytes(pixelDataSize))
        texInfoList.append((width,height,texType,texID,unkID))
    for i in range(numPalettes):
        numColors = bs.readUShort()
        palID = bs.readUByte() & 0xf
        unk = bs.readUByte()
        if numColors:
            pals.append(bs.readBytes(numColors*2))
            texPalInfoList.append((numColors,palID,unk))
        else:
            break        
    for i in range(numTextures):
        pixelIndex = i
        pixel = pixels[pixelIndex]
        width = texInfoList[pixelIndex][0]
        height = texInfoList[pixelIndex][1]
        for p in range(numPalettes):            
            palIndex = p
            palette = pals[palIndex]

            if (texInfoList[pixelIndex][2]==0) and( len(palette) == 512):
                textureData = rapi.imageDecodeRawPal(pixel,palette,width,height,8,"r5 g5 b5 p1")
                texList.append(NoeTexture(str(pixelIndex)+"_palID_"+str(palIndex), width, height, textureData, noesis.NOESISTEX_RGBA32))
            elif (texInfoList[pixelIndex][2]==0) and( len(palette) == 256):
                textureData = rapi.imageDecodeRawPal(pixel,palette,width,height,8,"r5 g5 b5 p1")
                texList.append(NoeTexture(str(pixelIndex)+"_palID_"+str(palIndex), width, height, textureData, noesis.NOESISTEX_RGBA32))                
            elif (texInfoList[pixelIndex][2]==0x80) and( len(palette) == 32):
                textureData = rapi.imageDecodeRawPal(pixel,palette,width,height,4,"r5 g5 b5 p1")
                texList.append(NoeTexture(str(pixelIndex)+"_palID_"+str(palIndex), width, height, textureData, noesis.NOESISTEX_RGBA32))
        
    return 1

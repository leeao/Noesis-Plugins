from inc_noesis import *


def registerNoesisTypes():
    handle = noesis.register("Mortal Kombat Special Forces PSX Texture txd", ".txd")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):

    return 1

def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    numTextures = bs.readInt()
    numPalettes = bs.readInt()
    numTexName = bs.readInt()
    texNames = []
    texPixelStartIDs = []
    texPalStartIDs = []
    for i in range(numTexName):
        skipOfs = bs.tell() + 16
        texName = bs.readString()
        texNames.append(texName)
        bs.seek(skipOfs)
        texPixelStartIDs.append(bs.readShort())
        texPalStartIDs.append(bs.readShort())
    
    pixels = []
    pals = []
    texInfoList = []
    texPalInfoList =[]
    for i in range(numTextures):
        bs.seek(bs.tell()+10)
        flag = bs.readShort()
        bs.seek(bs.tell()-12)
        if (flag != -1):
            unkTexID = bs.readShort()
        unk1 = bs.readUByte()
        unk2 = bs.readUByte()
        unk3 = bs.readUByte()
        texType = bs.readUByte()
        width = bs.readUByte()
        x1 = bs.readUByte()
        height = bs.readUByte()
        y1 = bs.readUByte()
        pixelDataSize = width * height
        if (texType==0x80):
            pixelDataSize //= 2
        texID = bs.readUByte()
        unkID = bs.readUByte()
        flag = bs.readShort()
        pixels.append(bs.readBytes(pixelDataSize))
        texInfoList.append((width,height,texType,texID,unkID))
    for i in range(numPalettes):
        numColors = bs.readUShort()
        palID = bs.readUByte() & 0xf
        unk = bs.readUByte()
        flag =  bs.readInt()
        if numColors:
            pals.append(bs.readBytes(numColors*2))
            texPalInfoList.append((numColors,palID,unk))
        else:
            break
    for i in range(numTexName):
        if i != (numTexName - 1):
            texPixelCount = texPixelStartIDs[i+1] - texPixelStartIDs[i]
            texPalCount = texPalStartIDs[i+1] - texPalStartIDs[i]
        else:
            texPixelCount = numTextures - texPixelStartIDs[i]
            texPalCount = len(pals) - texPalStartIDs[i]
        for j in range(texPixelCount):
            pixelIndex = texPixelStartIDs[i] + j
            #palIndex = texPalStartIDs[i]
            pixel = pixels[pixelIndex] 
            #palette = pals[palIndex]
            width = texInfoList[pixelIndex][0]
            height = texInfoList[pixelIndex][1]
            for p in range(texPalCount):
                palIndex = texPalStartIDs[i] + p
                palette = pals[palIndex] 
                if (texInfoList[pixelIndex][2]==0) and( len(palette) == 512):
                    textureData = rapi.imageDecodeRawPal(pixel,palette,width,height,8,"r5 g5 b5 p1")
                    texList.append(NoeTexture(texNames[i]+"_texID_"+str(pixelIndex)+"_palID_"+str(palIndex-p)+"_"+str(p), width, height, textureData, noesis.NOESISTEX_RGBA32))
                elif (texInfoList[pixelIndex][2]==0x80) and( len(palette) == 32):
                    textureData = rapi.imageDecodeRawPal(pixel,palette,width,height,4,"r5 g5 b5 p1")
                    texList.append(NoeTexture(texNames[i]+"_texID_"+str(pixelIndex)+"_palID_"+str(palIndex-p)+"_"+str(p), width, height, textureData, noesis.NOESISTEX_RGBA32))

    return 1

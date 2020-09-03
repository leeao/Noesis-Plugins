#by Allen

from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("Torus Games monster jam urban assault .txs textures ", ".txs")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)

	return 1

decodeSize = (8,16,32,64,128,256,512,1024,8,16,32,64,128,256,512,1024)

def noepyCheckType(data):
        bs = NoeBitStream(data)
        magic = bs.readInt()
        if magic != 0x10007:
            return 0
        return 1

def noepyLoadRGBA(data, texList):
        bs = NoeBitStream(data)
        magic = bs.readInt()
        numTex = bs.readInt()
        texNameList = []
        offsetList = []
        for i in range(numTex):
                offsetList.append(bs.readInt())
        for i in range(numTex):
                texNameLen = bs.readUByte()
                texName = noeStrFromBytes(bs.readBytes(texNameLen))
                texNameList.append(texName)
        baseOfs = bs.tell()
        for i in range(numTex):
                bs.seek(baseOfs + offsetList[i])
                pixelSize = bs.readInt()                        
                palSize = bs.readInt()                
                unk = bs.readShort()
                widthFlag = (bs.readUByte() >> 4) & 0xf
                unkFlag = bs.readUByte()
                alphaFlag = (unkFlag >> 4) & 0xf
                unk2 = bs.readInt()
                pixels = bs.readBytes(pixelSize)
                palette = bs.readBytes(palSize)

                logSize = pixelSize
                if palSize == 32:
                        logSize *= 2

                width = decodeSize[widthFlag]
                height = logSize // width
                
                palFormat = "r5g5b5p1"

                if palSize == 32:
                        textureData = rapi.imageDecodeRawPal(pixels,palette,width,height,4,palFormat)
                        texList.append(NoeTexture(texNameList[i], width, height, textureData, noesis.NOESISTEX_RGBA32))
                elif palSize == 512:
                        textureData = rapi.imageDecodeRawPal(pixels,palette,width,height,8,palFormat)
                        texList.append(NoeTexture(texNameList[i], width, height, textureData, noesis.NOESISTEX_RGBA32))
        return 1

#Kingdom Under Fire II .vap textures Noesis Importer.
#By Allen
from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("Kingdom Under Fire II .vap textures", ".vap")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)

	noesis.logPopup()
	return 1
def noepyCheckType(data):
        bs = NoeBitStream(data)
        id1 = bs.readInt()
        id2 = bs.readInt()
        if id1 != 1 or id2 != 1:
            return 0
        return 1
def noepyLoadRGBA(data, texList):
        bs = NoeBitStream(data)	
        ctx = rapi.rpgCreateContext()
        
        idstring = bs.readInt()
        version  = bs.readInt()
        numTex = bs.readInt()
        for i in range(numTex):
            unk1 = bs.readInt()
            unk2 = bs.readInt()
            fileIndex = bs.readInt()
            unk3 = bs.readInt()
            
            width  = bs.readShort()
            height = bs.readShort()
            unkFlag = bs.readShort()
            texType = bs.readShort()
            pixelDataSize = bs.readInt()
            texData = bs.readBytes(pixelDataSize)
            texFormat = 0
            if texType == 0:
                texFormat = noesis.NOESISTEX_DXT1
            elif texType == 4:
                texFormat = noesis.NOESISTEX_DXT5
            elif texType == 133:
                texData = rapi.imageDecodeRaw(texData,width,height,"R8A8")
                texFormat = noesis.NOESISTEX_RGBA32                  
            elif texType == 176:
                texFormat = noesis.NOESISTEX_RGB24                
            else:
                print("can't support foramt:",texType)
            if texFormat != 0:
                texture = NoeTexture(str(fileIndex), width, height, texData, texFormat)
                texList.append(texture)
        
        return 1
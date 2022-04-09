#VectorUnit Games Android textures Noesis Importer.
#By Allen
from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("VectorUnit Games Android textures",".vap;.ttf;.dat")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)

	noesis.logPopup()
	return 1
def noepyCheckType(data):
    return 1
def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)	
    ctx = rapi.rpgCreateContext()
    bs.seek(0x15)
    texFormat = bs.readInt()
    width = bs.readInt()
    height = bs.readInt()
    MipMaps = bs.readInt()
    dataSize = bs.readInt()
    pixelBuff = bs.readBytes(dataSize)
    if texFormat == 0x24:
        texData = rapi.imageDecodeETC(pixelBuff, width, height,"RGBA")      
    elif texFormat == 0x23:
        texData = rapi.imageDecodeETC(pixelBuff, width, height,"RGBA1")     
    elif texFormat == 0x10:
        texData = rapi.imageDecodeETC(pixelBuff, width, height,"RGB")
    elif texFormat == 0x5:    
        texData = pixelBuff
    texture = NoeTexture(rapi.getInputName() , width, height, texData, noesis.NOESISTEX_RGBA32)
    texList.append(texture)

    return 1
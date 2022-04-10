#By Allen
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Moshi Monsters Village iOS .moimage textures", ".moimage")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1
def noepyCheckType(data):
        bs = NoeBitStream(data)
        return 1	
def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)	
    ctx = rapi.rpgCreateContext()

    idstring = bs.readBytes(4)
    unk1 = bs.readInt()
    width = bs.readInt()
    height = bs.readInt()
    texFormat = bs.readInt()
    unk3 = bs.readInt()
    unk4 = bs.readInt()
    unk5 = bs.readInt()
    decompSize = bs.readInt()
    zipSize = bs.readInt()

    zipData = bs.readBytes(zipSize)	
    texData = rapi.decompInflate(zipData,decompSize)
    
    if texFormat == 3:
        texData = rapi.imageDecodeRaw(texData,width,height,"B5G6R5")        
    elif texFormat == 4:
        texData = rapi.imageDecodeRaw(texData,width,height,"A4B4G4R4")
  
    #elif texForamt == 6:
    #    texPixelFormat = "RGBA32"
    
    texture = NoeTexture(rapi.getInputName(), width, height, texData, noesis.NOESISTEX_RGBA32)
    texList.append(texture)
    
    return  1		

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Monster Hunter Explore MHXR Android Textures", ".tex")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1
def noepyCheckType(data):
        bs = NoeBitStream(data)
        idstring = bs.readBytes(4)
        if idstring != b'\x54\x45\x58\x20':
                return 0
        return 1	
def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)	
    ctx = rapi.rpgCreateContext()
    
    idstring = bs.readInt()
    flag1 = bs.readInt()
    flag2 = bs.readInt() 
    flag3 = bs.readUInt()
    width = (flag3 & 0x1FFF) 
    height = ((flag3 >> 13) & 0x1FFF) 
    offset1 = bs.readInt()
    offset2 = bs.readInt()
    offset3 = bs.readInt()
    astcSize = bs.readInt()
    pvrtcDataSize = bs.readInt()
    dxt5DataSize = bs.readInt()
    texVersion = flag1 & 0xff
    
    texFormat = (flag1 >> 16) & 0xFF
    
    if pvrtcDataSize > 0 and dxt5DataSize > 0:         
        bs.seek(offset2)
    else:
        bs.seek(offset1)

    if texFormat == 13:
            pixelBuff = bs.readBytes(pvrtcDataSize)
            texData = rapi.imageDecodePVRTC(pixelBuff, width, height, 4)
            print("PVRTC")
    elif texFormat == 10:
            pixelBuff = bs.readBytes(bs.getSize()-0x28)
            texData = rapi.imageDecodeETC(pixelBuff, width, height, "RGB")
            print("ETC")
    elif texFormat == 7:
            pixelBuff = bs.readBytes(bs.getSize()-0x28)  
            texData   = rapi.imageDecodeRaw(pixelBuff, width, height,"A4B4G4R4")        
            print("ABGR4444")    
    texture = NoeTexture(rapi.getInputName(), width, height, texData, noesis.NOESISTEX_RGBA32)
    texList.append(texture)
    
    return  1		

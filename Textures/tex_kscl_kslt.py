#By Allen
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("KSCL Layout textures", ".kscl;.kslt")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1
def noepyCheckType(data):
        bs = NoeBitStream(data)
        idstring = bs.readBytes(4)
        if idstring not in [b'LCSK' , b'TLSK'] :
                return 0
        return 1	
def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)	
    ctx = rapi.rpgCreateContext()

    magic = bs.readBytes(4)
    bs.seek(0)
    if magic == b'LCSK':        
        ksclMagic = bs.readBytes(8) #KSCL
        ksclFileSize = bs.readInt()
        bs.seek(ksclFileSize)
        
        ksltBaseOfs = bs.tell()    
        ksltMagic = bs.readInt() #0x100
        bs.seek(20,NOESEEK_REL)
        ksltOffset = bs.readInt()
        bs.seek(ksltBaseOfs+ksltOffset+20)
        
        ksltMaigc = bs.readInt() #KSLT    
        bs.seek(8,NOESEEK_REL)
        ksltDataSize = bs.readInt()
        unk = bs.readInt()
        tlskFileSize = bs.readInt()
    
    
    tlskBaseOfs = bs.tell()
    tlskMaigc = bs.readBytes(8) #TLSK
    numFiles = bs.readInt()
    tlskDataSize = bs.readInt()
    unkFloatsSize = bs.readInt()
    unk2 = bs.readInt()
    numFiles2 = bs.readInt()
    bs.seek(36+unkFloatsSize,NOESEEK_REL)
    
    offsetList = []
    
    for i in range(numFiles):
        
        offsetList.append(bs.readInt())
        bs.seek(16,NOESEEK_REL)
    
    nameList = []
    
    for i in range(numFiles):
        nameList.append(bs.readString())
    
    for i in range(numFiles):
        bs.seek(offsetList[i]+tlskBaseOfs)
        texFormat = bs.readInt()
        width = bs.readShort()
        height = bs.readShort()
        bs.seek(20,NOESEEK_REL)
        pixelDataSize = bs.readInt()
        lineSize = bs.readInt()
        bs.seek(36,NOESEEK_REL)
        
        pixelBuff = bs.readBytes(pixelDataSize)
        
        #print(i,texFormat,nameList[i])
        
        if texFormat == 0:
            texData = rapi.imageDecodeRaw(pixelBuff,width,height,"B8G8R8A8")
        elif texFormat == 3:
            texData = rapi.imageDecodeDXT(pixelBuff, width, height, noesis.NOESISTEX_DXT5)
        else:            
            print("Can't support format:",texFormat)            
        texture = NoeTexture(nameList[i], width, height, texData, noesis.NOESISTEX_RGBA32)
        texList.append(texture)  

    
    return  1		

from inc_noesis import *
import lib_zq_nintendo_tex as nintex

def registerNoesisTypes():
    handle = noesis.register("Manhunt 2 WII textures", ".txd")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):
    bs = NoeBitStream(data)
    bs.setEndian(NOE_BIGENDIAN)
    idstring = noeStrFromBytes(bs.readBytes(4))
    if idstring == "MH2Z":
        decomSize = bs.readUInt() 
        comSize = bs.getSize() - 8
        comBuffer = bs.readBytes(comSize)
        deComBuffer = rapi.decompInflate(comBuffer,decomSize)
        bs = NoeBitStream(deComBuffer)
        bs.setEndian(NOE_BIGENDIAN)
        idstring = noeStrFromBytes(bs.readBytes(4))
    if idstring != "TDCT":
        return 0
    return 1
def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    bs.setEndian(NOE_BIGENDIAN)
    idstring = noeStrFromBytes(bs.readBytes(4))
    if idstring == "MH2Z":
        decomSize = bs.readInt()
        comSize = bs.getSize() - 8
        comBuffer = bs.readBytes(comSize)
        deComBuffer = rapi.decompInflate(comBuffer,decomSize)
        bs = NoeBitStream(deComBuffer)
        bs.setEndian(NOE_BIGENDIAN) 
    bs.seek(0x20)
    numTextures = bs.readInt()
    firstTexOffset = bs.readInt()
    lastTexOffset = bs.readInt()
    
    bs.seek(firstTexOffset)
    nextOffset=0
    index = 0
    while(nextOffset!=0x24):
        curOffset = bs.tell()
        nextOffset = bs.readInt()
        prevOffset = bs.readInt()
        skipSize = bs.tell()+120
        textureName = bs.readString()      
        bs.seek(skipSize)
        pixelDataOffset= bs.readInt()
        unk = bs.readInt()
        bs.setEndian(NOE_LITTLEENDIAN)
        pixelDataSize = bs.readInt()
        bs.setEndian(NOE_BIGENDIAN)
        
        bs.seek(pixelDataOffset)
        chunkFlag = bs.readInt()
        numData = bs.readInt()
        unk = bs.readInt()
        texInfo=[]
        for i in range(numData):
            headerOffset = bs.readInt() + pixelDataOffset
            bs.readInt()
            nextOfs = bs.tell()
            
            bs.seek(headerOffset)
            height = bs.readUShort()
            width = bs.readUShort()
            texFormat = bs.readInt()
            pixelOffset = bs.readInt()
            texInfo.append((width,height,pixelOffset,texFormat))
            
            bs.seek(nextOfs)
        dataSizeList = []
        texDataList = []
        for i in range(numData):
            if numData==2:
                if i == 0:
                    singleDataSize = texInfo[i+1][2] - texInfo[i][2]
                else:
                    singleDataSize = pixelDataSize -  texInfo[i][2]
                    textureName = textureName +"_Alpha"
            else:
                singleDataSize = pixelDataSize - texInfo[i][2]
            dataSizeList.append(singleDataSize)
            
            #if(numData>1):
            #    print(index,'%x'% (pixelDataOffset+texInfo[i][2]),"Size:",singleDataSize,textureName)
            
            bs.seek(pixelDataOffset+texInfo[i][2])
            pixel = bs.readBytes(singleDataSize)
            texture = nintex.convert(pixel, texInfo[i][0], texInfo[i][1], texInfo[i][3])
            texture.name = textureName
            texList.append(texture)
            texDataList.append(texture)
            index += 1
        bs.seek(nextOffset)     
    return 1

#Idea Factroy .cl3 and .tid textures Noesis Importer.
#By Allen
from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("Idea Factroy .tid textures", ".tid")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
	handle = noesis.register("Idea Factroy .cl3  textures", ".cl3")
	noesis.setHandlerTypeCheck(handle, noepyCL3LCheckType)
	noesis.setHandlerLoadRGBA(handle, noepyCL3LLoadRGBA)
	noesis.logPopup()
	return 1
def noepyCheckType(data):
        bs = NoeBitStream(data)
        magic = bs.readUInt()
        if magic != 0x90444954:
            return 0
        return 1
def noepyLoadRGBA(data, texList):        
    ctx = rapi.rpgCreateContext()
    tex = readTid(data)
    if tex != 0:
        texList.append(tex)

    return 1
def noepyCL3LCheckType(data):
        bs = NoeBitStream(data)
        magic = bs.readUInt()
        if magic != 0x4C334C43:
            return 0
        return 1
def noepyCL3LLoadRGBA(data, texList):        
    ctx = rapi.rpgCreateContext()
    tex = readCL3L(data,texList)
        
    return 1    
def readJpStr(strBytes):
    strLen = 0
    for i in range( len(strBytes)):
        if strBytes[i] != 0:
            strLen += 1
        else:
            break
    jpStrBytes = bytearray(strLen)
    jpStrBytes[0:strLen] = strBytes[0:strLen]
    utf8Bytes = jpStrBytes.decode('shift-jis').encode('utf-8') 
    jpStr = str(utf8Bytes)
    return jpStr
def readTid(data):
    bs = NoeBitStream(data)	
    magic = bs.readInt()
    fileSize = bs.readInt()
    dataOffset = bs.readInt()
    unk1 = bs.readInt()
    unk2 = bs.readInt()
    unk3 = bs.readInt()
    bs.seek(8,NOESEEK_REL)
    
    #skipOfs = bs.tell() + 32    
    texName = readJpStr(bs.readBytes(32))
    #print(texName)
    #bs.seek(skipOfs)

    unk4 = bs.readInt()
    width = bs.readInt()
    height = bs.readInt()
    unk5 = bs.readInt()
    
    unk6 = bs.readShort()
    unk7 = bs.readShort()
    unk8 = bs.readInt()
    dataSize = bs.readUInt()
    pixelOffset = bs.readUInt()
    
    unk9 = bs.readInt()
    fourCC = bs.readBytes(4)
    unk10 = bs.readInt()
    unk11 = bs.readInt()
    
    unk12 = bs.readInt()
    unk13 = bs.readInt()
    unk14 = bs.readInt()
    unk15 = bs.readInt()
    
    bs.seek(pixelOffset)
    pixelBuffer = bs.readBytes(dataSize)
    texFormat = 0
    if fourCC == b'DXT1':
        texFormat = noesis.NOESISTEX_DXT1
    elif fourCC == b'DXT5':
        texFormat = noesis.NOESISTEX_DXT5
    else:
        print("unknown format:",fourCC,pixelOffset)
    if texFormat != 0:
        texture = NoeTexture("tid", width, height, pixelBuffer, texFormat)
        return texture
    else:
        return 0
        
def readCL3L(data,texList):
    bs = NoeBitStream(data)	
    magic = bs.readInt()
    unk = bs.readInt()
    unk2 = bs.readInt()
    unk3 = bs.readInt()
    dataOfs = bs.readInt()
    bs.seek(dataOfs)
    FILE_COLLECTION = str(bs.readBytes(32).decode())
    numFile = bs.readInt()
    dataSize = bs.readInt()
    firstFileOffset = bs.readInt()
    bs.seek(firstFileOffset)
    for i in range(numFile):
        fileName = str(bs.readBytes(512).decode('shift-jis').encode('utf-8'))
        unk = bs.readInt()
        fileOffset = bs.readUInt() + firstFileOffset
        fileSize = bs.readUInt()
        bs.seek(36,NOESEEK_REL)
        nextOfs = bs.tell()
        bs.seek(fileOffset)
        fileData = bs.readBytes(fileSize)
        if fileData[0:4] == b'\x54\x49\x44\x90':
            bs.seek(fileOffset)
            tex = readTid(fileData)
            if tex != 0:
                texList.append(tex)
        elif fileData[0:4] == b'\x43\x4C\x33\x4c':
            readCL3L(fileData,texList)
        bs.seek(nextOfs)
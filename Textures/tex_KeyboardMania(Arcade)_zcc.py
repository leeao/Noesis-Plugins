#Author: Allen
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("KeyboardMania (Arcade) .zcc textures", ".zcc")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):
    bs = decodeLZSS(data)
    #bs = NoeBitStream(data)
    idstring = noeStrFromBytes(bs.readBytes(4))
    if idstring != "GCCF":
        return 0
    return 1
def decodeLZSS(data):
    bs = NoeBitStream(data)
    decomSize = bs.readUInt() 
    comSize = bs.getSize() - 4
    comBuffer = bs.readBytes(comSize)
    deComBuffer = rapi.decompLZS01(comBuffer,decomSize)
    bs = NoeBitStream(deComBuffer)
    return bs
def noepyLoadRGBA(data, texList):
    bs = decodeLZSS(data)
    #bs = NoeBitStream(data)
    bs.setEndian(NOE_BIGENDIAN)
    idstring = noeStrFromBytes(bs.readBytes(4))
    unk = bs.readShort()
    width = bs.readUShort()
    height = bs.readUShort()
    zero = bs.readShort()
    headerSize = bs.readInt()
    fileSize = bs.readInt()

    unk = bs.readShort()
    unk = bs.readShort()
    unk = bs.readShort()
    numSplitNames = bs.readShort()
    splitNameOfs = bs.readShort()
    zero = bs.readShort()
    unk = bs.readShort()
    unkNum = bs.readShort()
    texIDsOfs = bs.readShort()
    zero = bs.readShort()
    
    bs.seek(headerSize)
    pixel = bs.readBytes(width*height*2)
    pixel = rapi.swapEndianArray(pixel,2)
    textureData = rapi.imageDecodeRaw(pixel,width,height,"b5g5r5p1")
    texList.append(NoeTexture(rapi.getInputName(), width, height, textureData, noesis.NOESISTEX_RGBA32))  
    
    bs.seek(splitNameOfs)
    splitTexNames = []
    for i in range(numSplitNames):
        nameEndOfs = bs.tell() + 12
        texName = bs.readString()
        splitTexNames.append(texName)
        bs.seek(nameEndOfs)
        unk = bs.readInt()
        xofs = bs.readShort()
        yofs = bs.readShort()
        splitWidth = bs.readShort()
        splitHeight = bs.readShort()
        
        splitPixel = bytearray(splitWidth * splitHeight * 4)
        length = splitWidth * 4
        for y in range(splitHeight):
            srcIndex = (y + yofs) * width * 4 + xofs * 4            
            dstIndex = y * splitWidth * 4
            splitPixel[dstIndex:dstIndex+length] = textureData[srcIndex:srcIndex+length]
        #texList.append(NoeTexture(texName, splitWidth, splitHeight, splitPixel, noesis.NOESISTEX_RGBA32))

        #left rotate 90
        newSplitPixel = bytearray(splitWidth * splitHeight * 4)
        newWidth = splitHeight
        newHeight = splitWidth
        for y in range(newHeight):
            for x in range(newWidth):
                srcIndex = x * splitWidth * 4 + (splitWidth - 1 - y) * 4
                dstIndex = y * newWidth * 4 + x * 4
                newSplitPixel[dstIndex:dstIndex+4] = splitPixel[srcIndex:srcIndex+4]
        texList.append(NoeTexture(texName, newWidth, newHeight, newSplitPixel, noesis.NOESISTEX_RGBA32))
               

    return 1

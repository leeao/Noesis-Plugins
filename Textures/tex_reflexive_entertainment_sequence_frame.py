# By Allen
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Reflexive entertainment Frame and Sequence textures", ".frame;.sequence")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)

    # noesis.logPopup()
    return 1
def noepyCheckType(data):
    return 1
        
def noepyLoadRGBA(data, texList):

    bs = NoeBitStream(data)
    name_Ext = rapi.getLocalFileName(rapi.getInputName())
    name = rapi.getExtensionlessName(name_Ext)
    path = rapi.getDirForFilePath(rapi.getInputName())

    
    if rapi.checkFileExt(rapi.getInputName(),".frame") == 1:
        u1 = bs.readUInt()
        u2 = bs.readUInt()
        readTex(bs,name,path,texList)

    elif rapi.checkFileExt(rapi.getInputName(),".sequence") == 1:
        bs.seek(0x9)
        checkIsFont = bs.readByte() # for Ricochet Xtreme
        bs.seek(0)
        if checkIsFont != 0x78:
            u1,u2,u3 = struct.unpack('3I',bs.readBytes(12))

        headerData = decompressZlibRes(bs)
        outFname = path + name + ".txt"

        outFile(headerData,outFname)
        readTex(bs,name,path,texList)


    return 1

def decompressZlibRes(bs):
    cmpflag = bs.readByte()
    if cmpflag == 1:
        zlibDataSize = bs.readUInt()
        unzlibDataSize = bs.readUInt()
        zlibDatas = bs.readBytes(zlibDataSize)
        unzlibDatas = rapi.decompInflate(zlibDatas,unzlibDataSize)        
        return unzlibDatas
    return None

def outFile(data,fileName):
    f = open(fileName, "wb")
    f.write(data)
    f.close()

def readTex(bs,outName,path,texList):
    texFormat = bs.readByte()

    if texFormat == 0:
        rgbJpgFileSize = bs.readUInt()
        jpgDatas = bs.readBytes(rgbJpgFileSize-4)

        f = open(path + outName + ".jpg", "wb")
        f.write(jpgDatas)
        f.close()

        unzlibDatas = decompressZlibRes(bs)
        # outFile(unzlibDatas,path + outName + ".alpha")

        tex = noesis.loadImageRGBA(path + outName + ".jpg")
        # texList.append(tex)

        decodeData = unzlibDatas
        rgbaData = rapi.imageGetTexRGBA(tex)
        
        # delta encode
        for i in range(1,len(decodeData)):
            t1 = decodeData[i]
            t2 = decodeData[i-1]
            t1 += t2
            tbytes = struct.pack("H",t1)
            decodeData[i] = tbytes[0]
        for i in range(len(rgbaData)//4):
            rgbaData[i*4+3] = decodeData[i]
        texName = outName
        texture = NoeTexture(texName, tex.width, tex.height, rgbaData, noesis.NOESISTEX_RGBA32)
        texList.append(texture)
        noesis.saveImageRGBA(path + outName + ".tga", texture)
        
    elif texFormat == 1:        
        unzlibDatas = decompressZlibRes(bs)
        width = bs.readInt()
        height = bs.readInt()
        # outFile(unzlibDatas,path + outName + ".decmp")
        decodeData = unzlibDatas
        numPixels = len(decodeData) // 4
        for i in range(1,numPixels):
            t1 = decodeData[i]
            t2 = decodeData[i-1]
            t1 += t2
            tbytes = struct.pack("H",t1)
            decodeData[i] = tbytes[0]
        for i in range(1,numPixels):
            t1 = decodeData[i + numPixels]
            t2 = decodeData[i - 1 + numPixels]
            t1 += t2
            tbytes = struct.pack("H",t1)
            decodeData[i + numPixels] = tbytes[0] 
        for i in range(1,numPixels):
            t1 = decodeData[i + numPixels * 2]
            t2 = decodeData[i - 1 + numPixels * 2]
            t1 += t2
            tbytes = struct.pack("H",t1)
            decodeData[i + numPixels * 2] = tbytes[0]    
        for i in range(1,numPixels):
            t1 = decodeData[i + numPixels * 3]
            t2 = decodeData[i - 1 + numPixels * 3]
            t1 += t2
            tbytes = struct.pack("H",t1)
            decodeData[i + numPixels * 3] = tbytes[0]                                                  
        # outFile(decodeData,path + outName + ".decmp2")

        
        rgbaData = bytearray(width*height*4)       
        for i in range(len(rgbaData)//4):
            rgbaData[i*4] = decodeData[i]
            rgbaData[i*4+1] = decodeData[i+numPixels]
            rgbaData[i*4+2] = decodeData[i+numPixels*2]
            rgbaData[i*4+3] = decodeData[i+numPixels*3]

        texture =  NoeTexture(outName, width, height, rgbaData, noesis.NOESISTEX_RGBA32)
        texList.append(texture)
        noesis.saveImageRGBA(path + outName + ".tga", texture)

        
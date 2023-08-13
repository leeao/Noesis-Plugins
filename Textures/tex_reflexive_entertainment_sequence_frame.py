# By Allen

'''
Support games:
    Ricochet Infinity PC
    Ricochet Xtreme PC
    Ricochet HD PS3
'''

from inc_noesis import *
from io import SEEK_END, TextIOWrapper

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
        checkPS3 = data[4:8]
        # PS3
        if checkPS3 == b'CSeq':
            infoSize = bs.readUInt()
            infoData = bs.readBytes(infoSize)
            outFname = path + name + ".txt"
            outFile(infoData,outFname)
            txt = open(outFname,"r")
            CSequenceFrameInfoListOffset =  getBlockDataOffset(txt,"CSequenceFrameInfoList")
            if CSequenceFrameInfoListOffset != -1:
                FrameInfosArrayOffset = getBlockDataOffset(txt,"Frame Infos=Array")
                if FrameInfosArrayOffset != -1:
                    txt.seek(FrameInfosArrayOffset)
                    txt.readline()
                    t = txt.readline().strip().split('=')
                    
                    if (t[0] == "Item Count"):
                        count = int(t[1])
                        for i in range(count):
                            offset = txt.tell()
                            data = dict()
                            readBlockParameter(txt, offset, data)
                            left = int(data.get('Left'))
                            right = int(data.get('Right'))
                            top = int(data.get('Top'))
                            bottom = int(data.get('Bottom'))
                            width = right - left
                            height = bottom - top
                            dxt5Data = bs.readBytes(width * height)                           
                            tex = NoeTexture(name+str(i), width, height, dxt5Data, noesis.NOESISTEX_DXT5)
                            texList.append(tex)
            txt.close()     
        # PC       
        else:
            bs.seek(0x9)
            checkIsFont = bs.readByte() # for Ricochet Xtreme
            bs.seek(0)
            if checkIsFont != 0x78:
                u1,u2,u3 = struct.unpack('3I',bs.readBytes(12))

            headerData = decompressZlibRes(bs)
            outFname = path + name + ".txt"

            outFile(headerData,outFname)
            readTex(bs,name,path,texList)

            txt = open(outFname,"r")
            CSequenceFrameInfoListOffset =  getBlockDataOffset(txt,"CSequenceFrameInfoList")
            if CSequenceFrameInfoListOffset != -1:
                FrameInfosArrayOffset = getBlockDataOffset(txt,"Frame Infos=Array")
                if FrameInfosArrayOffset != -1:
                    txt.seek(FrameInfosArrayOffset)
                    txt.readline()
                    t = txt.readline().strip().split('=')
                    
                    if (t[0] == "Item Count"):
                        count = int(t[1])
                        for i in range(count):
                            offset = txt.tell()
                            data = dict()
                            readBlockParameter(txt, offset, data)
                            left = int(data.get('Left'))
                            right = int(data.get('Right'))
                            top = int(data.get('Top'))
                            bottom = int(data.get('Bottom'))                            
                            tex = crop32(texList[0].pixelData, name+str(i),texList[0].width, texList[0].height, left, right, top, bottom)
                            texList.append(tex)
            txt.close()


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

def outFile(data, fileName):
    f = open(fileName, "wb")
    f.write(data)
    f.close()

def readTex(bs, outName, path, texList):
    texFormat = bs.readByte()

    if texFormat == 0:
        rgbJpgFileSize = bs.readUInt()
        jpgDatas = bs.readBytes(rgbJpgFileSize-4)
        outFile(jpgDatas,path + outName + ".jpg")

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
        back = bs.tell()
        bs.seek(back + 9)
        checkOldVersion = bs.readUByte()
        bs.seek(back)
        # PC
        if checkOldVersion == 0x78:
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
        # PS3
        else:
            size = bs.readUInt()
            rgbaData = bs.readBytes(size)
            width = bs.readInt()
            height = bs.readInt()
            texture =  NoeTexture(outName, width, height, rgbaData, noesis.NOESISTEX_RGBA32)
            texList.append(texture)
            noesis.saveImageRGBA(path + outName + ".tga", texture)

def crop32(rgbadata, outName, width, height, left, right, top, bottom):
    cropWidth = right - left
    cropHeight = bottom - top
    lineSize = width * 4
    cropLineSize = cropWidth * 4
    outRgbaBuffer = bytes()  
    
    for y in range(top, bottom):
        baseOfs = y * lineSize + left * 4
        outRgbaBuffer += rgbadata[baseOfs : baseOfs + cropLineSize]
    return  NoeTexture(outName, cropWidth, cropHeight, outRgbaBuffer, noesis.NOESISTEX_RGBA32)


def getBlockDataOffset(txt:TextIOWrapper, blockName:str):  
    txt.seek(0) 
    while(1):
        text = txt.readline().strip() 
        if text == blockName:
            return txt.tell()                         
    return -1
    
def readBlockParameter(txt:TextIOWrapper, offset, parameterList:dict):
    txt.seek(offset)
    flag = 1
    while(flag):          
        text = txt.readline().strip()
        if text[0] == '}': break
        if text[0] != '{':
            textArray = text.split('=')             
            parameterList[str(textArray[0])] = textArray[1]

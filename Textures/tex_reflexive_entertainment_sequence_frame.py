# By Allen

'''
Support games:
    Big Kahuna Reef 1
    Big Kahuna Reef 2
    Big Kahuna Reef 3
    Big Kahuna Party
    Big Kahuna Words
    Build in time
    Costume Chaos
    Monarch
    Mosaic
    Ricochet HD PS3
    Ricochet Infinity
    Ricochet Infinity IOS
    Ricochet Lost Worlds
    Ricochet Recharged
    Ricochet Xtreme
    Swarm Gold
    Wik
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
            if bs.tell() >= bs.getSize():
                print("No bitmap.")        
                return 0            
            txt = open(outFname,"r")
            CSequenceOffset = getBlockDataOffset(txt,"CSequence")
            ddsFormat = 0
            useDDS = -1
            usdRaw32 = -1
            if CSequenceOffset != -1:
                header = dict()
                readBlockParameter(txt, CSequenceOffset, header)            
                if 'DDS' in header: ddsFormat = int(header.get('DDS'))
                else:
                    useDDS = getBlockDataOffset(txt,"DDS=1")
                    if useDDS == -1:
                        useRaw32 = getBlockDataOffset(txt,"DDS=0")
                    else:
                        ddsFormat = 1
            
            if ddsFormat == 0:
                format = bs.readByte()
                if format == 1:
                    dataSize = bs.readUInt()
                    rgbadata = bs.readBytes(dataSize)
                    width = bs.readInt()
                    height = bs.readInt()
                    tex = NoeTexture(name, width, height, rgbadata, noesis.NOESISTEX_RGBA32)
                    texList.append(tex)
            
            CSequenceFrameInfoListOffset =  getBlockDataOffset(txt,"CSequenceFrameInfoList")
            if CSequenceFrameInfoListOffset != -1:
                FrameInfosArrayOffset = getBlockDataOffset(txt,"Frame Infos=Array")
                if FrameInfosArrayOffset != -1:
                    txt.seek(FrameInfosArrayOffset)
                    txt.readline()
                    t = txt.readline().strip().split('=')
                    
                    if (t[0] == "Item Count"):
                        count = int(t[1])
                        arrayOffset = txt.tell()                                                
                        UpperLeftXOffsets = []
                        UpperLeftYOffsets = []

                        for i in range(count):
                            offset = txt.tell()
                            data = dict()
                            t = txt.readline().strip().split('=')
                            if (t[0] == "Frame Info") and (t[1] =="CFrameInfo"):
                                readBlockParameter(txt, offset, data)
                                if 'UpperLeftXOffset' in data:
                                    UpperLeftXOffset = int(data['UpperLeftXOffset'])
                                    UpperLeftXOffsets.append(UpperLeftXOffset)
                                if 'UpperLeftYOffset' in data:
                                    UpperLeftYOffset = int(data['UpperLeftYOffset'])
                                    UpperLeftYOffsets.append(UpperLeftYOffset)
                                # print(UpperLeftXOffset,UpperLeftYOffset)
                        baseXOffset = min(UpperLeftXOffsets)
                        baseYOffset = min(UpperLeftYOffsets)
                        # print("base:",baseXOffset,baseYOffset)
                        txt.seek(arrayOffset)
                        for i in range(count):
                            offset = txt.tell()
                            data = dict()
                            t = txt.readline().strip().split('=')
                            if (t[0] == "Frame Info") and (t[1] =="CFrameInfo"):
                                readBlockParameter(txt, offset, data)
                                if 'Left' in data: left = int(data.get('Left')) 
                                else: left = 0
                                right = int(data.get('Right'))
                                if 'Top' in data: top = int(data.get('Top'))
                                else: top = 0
                                bottom = int(data.get('Bottom'))
                                width = right - left
                                height = bottom - top
                                if ddsFormat:
                                    storageWidth = getDxtStorageSize(width)
                                    storageHeight = getDxtStorageSize(height)
                                    dxtData = bs.readBytes(storageWidth * storageHeight)
                                    rgbaData = rapi.imageDecodeDXT(dxtData, storageWidth, storageHeight, noesis.NOESISTEX_DXT5)
                                    tex = crop32(rgbaData, name+str(i), storageWidth, storageHeight, 0, width, 0, height)
                                    # tex = NoeTexture(name+str(i), width, height, dxtData, noesis.NOESISTEX_DXT5)
                                    # texList.append(tex)
                                    xOffset = 0
                                    yOffset = 0
                                    if 'UpperLeftXOffset' in data:
                                        UpperLeftXOffset = int(data['UpperLeftXOffset'])
                                        xOffset = UpperLeftXOffset - baseXOffset
                                    if 'UpperLeftYOffset' in data:
                                        UpperLeftYOffset = int(data['UpperLeftYOffset'])
                                        yOffset = UpperLeftYOffset - baseYOffset
                                    # print("x y offset:",xOffset,yOffset)
                                    if xOffset != 0 or yOffset != 0:                                    
                                        padRgbaData =  paddingPixel32(tex.pixelData, xOffset, yOffset, tex.width, tex.height)
                                        tex = NoeTexture(name+str(i), xOffset + tex.width, yOffset + tex.height, padRgbaData, noesis.NOESISTEX_RGBA32)
                                        texList.append(tex)
                                    else:
                                        texList.append(tex)                                    
                                else:
                                    tex = crop32(texList[0].pixelData, name+str(i),texList[0].width, texList[0].height, left, right, top, bottom)
                                    # texList.append(tex)
                                    xOffset = 0
                                    yOffset = 0
                                    if 'UpperLeftXOffset' in data:
                                        UpperLeftXOffset = int(data['UpperLeftXOffset'])
                                        xOffset = UpperLeftXOffset - baseXOffset
                                    if 'UpperLeftYOffset' in data:
                                        UpperLeftYOffset = int(data['UpperLeftYOffset'])
                                        yOffset = UpperLeftYOffset - baseYOffset
                                    # print("x y offset:",xOffset,yOffset)
                                    if xOffset != 0 or yOffset != 0:                                    
                                        padRgbaData =  paddingPixel32(tex.pixelData, xOffset, yOffset, tex.width, tex.height)
                                        tex = NoeTexture(name+str(i), xOffset + tex.width, yOffset + tex.height, padRgbaData, noesis.NOESISTEX_RGBA32)
                                        texList.append(tex)
                                    else:
                                        texList.append(tex)                                    
                                    
                    # single frame
                    elif (t[0] == "Frame Info") and (t[1] =="CFrameInfo"):
                        offset = txt.tell()
                        data = dict()                        
                        readBlockParameter(txt, offset, data)
                        if 'Left' in data: left = int(data.get('Left')) 
                        else: left = 0
                        right = int(data.get('Right'))
                        if 'Top' in data: top = int(data.get('Top'))
                        else: top = 0
                        bottom = int(data.get('Bottom'))
                        width = right - left
                        height = bottom - top
                        if ddsFormat:
                            storageWidth = getDxtStorageSize(width)
                            storageHeight = getDxtStorageSize(height)
                            dxtData = bs.readBytes(storageWidth * storageHeight)
                            tex = NoeTexture(name, width, height, dxtData, noesis.NOESISTEX_DXT5)
                            texList.append(tex)
                        else:
                            if texList[0].width != (right - left) or texList[0].height != (bottom - top):   
                                texture = crop32(texList[0].pixelData, name,texList[0].width, texList[0].height, left, right, top, bottom)
                                texList.append(texture)
                                noesis.saveImageRGBA(path + name + "_crop" + ".tga", texture)
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
            if bs.tell() >= bs.getSize():
                print("No bitmap.")        
                return 0
            readTex(bs,name,path,texList)

            txt = open(outFname,"r")
            CSequenceFrameInfoListOffset =  getBlockDataOffset(txt,"CSequenceFrameInfoList")
            if CSequenceFrameInfoListOffset != -1:
                FrameInfosArrayOffset = getBlockDataOffset(txt,"Frame Infos=Array")
                if FrameInfosArrayOffset != -1:
                    txt.seek(FrameInfosArrayOffset)
                    txt.readline()
                    t = txt.readline().strip().split('=')
                    # multi frame
                    if (t[0] == "Item Count"):
                        count = int(t[1])
                        arrayOffset = txt.tell()                                                
                        UpperLeftXOffsets = []
                        UpperLeftYOffsets = []

                        for i in range(count):
                            offset = txt.tell()
                            data = dict()
                            t = txt.readline().strip().split('=')
                            if (t[0] == "Frame Info") and (t[1] =="CFrameInfo"):
                                readBlockParameter(txt, offset, data)
                                if 'UpperLeftXOffset' in data:
                                    UpperLeftXOffset = int(data['UpperLeftXOffset'])
                                    UpperLeftXOffsets.append(UpperLeftXOffset)
                                if 'UpperLeftYOffset' in data:
                                    UpperLeftYOffset = int(data['UpperLeftYOffset'])
                                    UpperLeftYOffsets.append(UpperLeftYOffset)
                                # print(UpperLeftXOffset,UpperLeftYOffset)
                        baseXOffset = min(UpperLeftXOffsets)
                        baseYOffset = min(UpperLeftYOffsets)
                        # print("base:",baseXOffset,baseYOffset)                  
                        txt.seek(arrayOffset)
                        for i in range(count):
                            offset = txt.tell()
                            data = dict()
                            t = txt.readline().strip().split('=')
                            if (t[0] == "Frame Info") and (t[1] =="CFrameInfo"):
                                readBlockParameter(txt, offset, data)
                                if 'Left' in data: left = int(data.get('Left')) 
                                else: left = 0
                                if 'Right' in data: right = int(data.get('Right'))
                                else: right = texList[0].width
                                if 'Top' in data: top = int(data.get('Top'))
                                else: top = 0
                                if 'Bottom' in data: bottom = int(data.get('Bottom'))
                                else: bottom = texList[0].height                         
                                tex = crop32(texList[0].pixelData, name+str(i),texList[0].width, texList[0].height, left, right, top, bottom)
                                xOffset = 0
                                yOffset = 0
                                if 'UpperLeftXOffset' in data:
                                    UpperLeftXOffset = int(data['UpperLeftXOffset'])
                                    xOffset = UpperLeftXOffset - baseXOffset
                                if 'UpperLeftYOffset' in data:
                                    UpperLeftYOffset = int(data['UpperLeftYOffset'])
                                    yOffset = UpperLeftYOffset - baseYOffset
                                # print("x y offset:",xOffset,yOffset)
                                if xOffset != 0 or yOffset != 0:                                    
                                    padRgbaData =  paddingPixel32(tex.pixelData, xOffset, yOffset, tex.width, tex.height)
                                    tex = NoeTexture(name+str(i), xOffset + tex.width, yOffset + tex.height, padRgbaData, noesis.NOESISTEX_RGBA32)
                                    texList.append(tex)
                                else:
                                    texList.append(tex)
                    # single frame
                    elif (t[0] == "Frame Info") and (t[1] =="CFrameInfo"):
                            offset = txt.tell()
                            data = dict()
                            readBlockParameter(txt, offset, data)
                            if 'Left' in data: left = int(data.get('Left')) 
                            else: left = 0
                            if 'Right' in data: right = int(data.get('Right'))
                            else: right = texList[0].width
                            if 'Top' in data: top = int(data.get('Top'))
                            else: top = 0
                            if 'Bottom' in data: bottom = int(data.get('Bottom'))
                            else: bottom = texList[0].height
                            if texList[0].width != (right - left) or texList[0].height != (bottom - top):                            
                                texture = crop32(texList[0].pixelData, name+str(i),texList[0].width, texList[0].height, left, right, top, bottom)
                                texList.append(texture)
                                noesis.saveImageRGBA(path + name + "_crop" + ".tga", texture)                     
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

        tex = noesis.loadImageRGBA(path + outName + ".jpg")

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

def getDxtStorageSize(value):
    outValue = value
    if (value % 4) > 0:
        outValue = value + 4 - (value % 4)
    return outValue


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

def paddingPixel32(rgbaData, xOffset, yOffset, srcWidth, srcHeight):
    padWidth = xOffset + srcWidth
    padHeight = yOffset + srcHeight
    outBuffer = bytes()
    if yOffset:
        for y in range(yOffset):            
            outBuffer += bytearray(padWidth * 4)
    for y in range(yOffset, padHeight):
        if xOffset:
            outBuffer += bytearray(xOffset * 4)
        lineSize = srcWidth * 4
        outBuffer += rgbaData[(y - yOffset) * lineSize:(y - yOffset + 1)*lineSize]
    return outBuffer


def getBlockDataOffset(txt:TextIOWrapper, blockName:str):  
    txt.seek(0,SEEK_END)
    fileSize = txt.tell()
    txt.seek(0) 
    while(txt.tell() < fileSize):
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

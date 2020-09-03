from inc_noesis import *
def registerNoesisTypes():
    handle = noesis.register("kater thps hawk .tex.ps2 textrues", ".ps2")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):
    if len(data) < 8:
	    return 0
    return 1
decodeTexSize=(1,2,4,8,16,32,64,128,256,512,1024,2048)

def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    texType = rapi.getInputName()[-7:]
    if texType == "tex.ps2":
        magic = bs.readInt()
        numGroup = bs.readInt()
        numTexCount = bs.readInt()
        for g in range(numGroup):
            unk = bs.readInt()
            bs.seek(8,1) #two zeros         
            numTextures = bs.readInt()        
            for i in range(numTextures):
                readTexture(bs,texList)
    elif texType == "img.ps2":
        readTexture(bs,texList)
    return 1

def readTexture(bs,texList):
    bs.readInt()
    bs.readInt()    
    width = decodeTexSize[bs.readInt()]
    height = decodeTexSize[bs.readInt()]
    bppFormat=bs.readInt() # 2=16bpp 0x13=8bpp 0x14=4bpp
    havePal = (bppFormat & 0xF0) >> 4
    palPixelForamt=bs.readInt()
    numMips=bs.readUShort()
    chunkFlag = bs.readUShort()            
    if bppFormat == 2:
        bpp = 16                
    elif bppFormat == 0x13:
        bpp = 8
        numColor = 256
    elif bppFormat == 0x14:
        bpp = 4
        numColor = 16
    if havePal:
        if palPixelForamt == 0:
            palFormat = "r8g8b8a8"
            palSize = numColor * 4
        elif palPixelForamt == 2:
            palFormat = "r5g5b5a1"
            palSize = numColor * 2
    if chunkFlag < 0x8000:        
        curOfs = bs.tell()
        if curOfs % 16:
            palLen = 16 - (curOfs % 16)
            bs.seek(palLen,1)
        if havePal:
            palette = bs.readBytes(palSize)
            newPal = bytearray(palSize)
            if palFormat == "r8g8b8a8":
                for p in range(numColor):
                    newPal[p*4] = palette[p*4]
                    newPal[p*4+1] = palette[p*4+1]
                    newPal[p*4+2] = palette[p*4+2]
                    newPal[p*4+3] = min(palette[p*4+3]*2, 255)
                palette = newPal
            pixel = bs.readBytes(width*height*bpp//8)
            if (width>8):
                pixel = rapi.imageUntwiddlePS2(pixel,width,height,bpp)                    
            textureData = rapi.imageDecodeRawPal(pixel,palette,width,height,bpp,palFormat)                        
        if bppFormat == 2:
            pixel = bs.readBytes(width*height*bpp//8)          
            textureData = rapi.imageDecodeRaw(pixel,width,height,"r5g5b5p1")  
        texList.append(NoeTexture(rapi.getInputName(), width, height, textureData, noesis.NOESISTEX_RGBA32))
        if numMips:
            for m in range(1,numMips+1):
                tw = width >> m
                th = height >> m
                tSize = tw * th * bpp // 8
                bs.seek(tSize,1)

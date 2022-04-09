from inc_noesis import *

# Thanks Zhenёq, Nintendo wii code reference
# https://github.com/Zheneq/Noesis-Plugins

# Format reference
# http://wiki.tockdom.com/wiki/Image_Formats


def registerNoesisTypes():
    handle = noesis.register("Angry Birds Trilogy WII Textures", ".gct")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):
    bs = NoeBitStream(data)
    idstring = noeStrFromBytes(bs.readBytes(4))
    if idstring != "MIPh":
        return 0
    return 1
def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    bs.setEndian(NOE_BIGENDIAN)    
    MIPhMagic = noeStrFromBytes(bs.readBytes(4)) #"MIPh"
    dataSize = bs.readInt()
    xoffset = bs.readShort()
    yoffset = bs.readShort()
    dataOfs = bs.readInt()
    width = bs.readInt()
    height = bs.readInt()
    unk0 = bs.readShort()
    unk1 = bs.readShort()
    unk2 = bs.readInt()
    gctMagic = noeStrFromBytes(bs.readBytes(4)) #"GCT "
    texWidth = bs.readShort()
    texHeight = bs.readShort()
    texFormat = bs.readShort()
    palFormat = bs.readShort() #-1=not use; 0=IA8; 1=RGB565; 2=RGB5A3;
    unk3 = bs.readInt()
    pixelSize = bs.readInt()
    palSize = bs.readInt()
    unk14 = bs.readInt()
    unk15 = bs.readInt()
    bs.seek(dataOfs)
    pixel = bs.readBytes(pixelSize)
    palette = readPalette(palFormat,palSize,bs)     
    if texFormat == 6:
        print("32BPP RGBA32")
        tile_w= 4
        tile_h= 4    
        textureData = read32RGBA(pixel,width,height,tile_w,tile_h)
        texList.append(NoeTexture(rapi.getInputName(), width, height, textureData, noesis.NOESISTEX_RGBA32))
        real_width,real_height = getRealWH(width,height,tile_w,tile_h) 
    elif(texFormat==8):     
        print("4BPP PAL4")    
        tile_w= 8
        tile_h= 8
        real_width,real_height = getRealWH(width,height,tile_w,tile_h) 
        c8pixel = convert4to8(pixel,real_width,real_height)
        untilePixel = untile(c8pixel,width,height,tile_w,tile_h,8)
        textureData = convert8to32(untilePixel,palette,width,height)
        texList.append(NoeTexture(rapi.getInputName(), width, height, textureData, noesis.NOESISTEX_RGBA32))
    elif texFormat == 9:
        print("8BPP PAL8")
        tile_w= 8
        tile_h= 4 
        c8pixel = untile(pixel,width,height,tile_w,tile_h,8)
        textureData = convert8to32(c8pixel,palette,width,height)
        texList.append(NoeTexture(rapi.getInputName(), width, height, textureData, noesis.NOESISTEX_RGBA32))
    return 1
def read32RGBA(pixel,width,height,tile_w,tile_h):
    real_width,real_height = getRealWH(width,height,tile_w,tile_h)
    tileSize = tile_w * tile_h * 4
    numTW = real_width // tile_w
    numTH = real_height // tile_h
    textureData = bytearray(real_width * real_height * 4)
    for y in range(0,real_height,tile_h):            
        for x in range(0,real_width,tile_w):                
            tileY_ID = y // tile_h
            tileX_ID = x // tile_w                
            dataPtr = tileY_ID * numTW * tileSize + tileSize * tileX_ID
            for ty in range(tile_h):
                for tx in range(tile_w):
                    dstIndex = (y + ty) * real_width*4 + (x + tx) * 4   
                    srcIndex = dataPtr + ty * tile_w * 2 + tx * 2
                    srcIndex2 = dataPtr + 32 + ty * tile_w * 2 + tx * 2
                    textureData[dstIndex]   = pixel[srcIndex+1]     #R
                    textureData[dstIndex+1] = pixel[srcIndex2]      #G
                    textureData[dstIndex+2] = pixel[srcIndex2+1]    #B
                    textureData[dstIndex+3] = pixel[srcIndex]       #A
    cropData = crop(textureData,real_width,real_height,width,height,32)
    return cropData
def readPalette(palFormat,palSize,bs):
    numColor = palSize // 2
    if palFormat == 0:
        palette = [ia8(bs.readUShort()) for i in range(numColor)]
    elif palFormat == 1:
        palette = [rgb565(bs.readUShort()) for i in range(numColor)]
    elif palFormat == 2:
        palette = [rgb5a3(bs.readUShort()) for i in range(numColor)]
    elif palFormat == -1:
        return 0
    else:
        print("unsupport palette format: ",palFormat)
        return 0
    return palette
def convert4to32(c4pixel,palette,width,height):
    c8pixel = bytearray(width*height)
    for i in range(width*height//2):
        index = c4pixel[i]
        id1 = (index >> 4) & 0xf
        id2 = index & 0xf
        c8pixel[i*2] = id1
        c8pixel[i*2+1] = id2  
    RGBA32Data = bytearray(width * height * 4)
    for i in range(width * height):
        RGBA32Data[i * 4:(i + 1) * 4] = palette[c8pixel[i]]         
    return RGBA32Data
def convert8to32(c8pixel,palette,width,height):
    RGBA32Data = bytearray(width * height * 4)
    for i in range(width * height):
        RGBA32Data[i * 4:(i + 1) * 4] = palette[c8pixel[i]]         
    return RGBA32Data
def convert4to8(c4pixel,real_width,real_height):
    c8pixel = bytearray(real_width*real_height)
    for i in range(real_width*real_height//2):
        index = c4pixel[i]
        id1 = (index >> 4) & 0xf
        id2 = index & 0xf
        c8pixel[i*2] = id1
        c8pixel[i*2+1] = id2
    return c8pixel
def untile(pixel,width,height,tile_w,tile_h,bpp):
    #bpp is bits per pixel
    #tile_w is tile width
    #tile_h is tile height
    real_width,real_height = getRealWH(width,height,tile_w,tile_h)
    numTileW = real_width // tile_w
    numTileH = real_height // tile_h
    lineSize = tile_w * bpp // 8
    tileSize = tile_w * tile_h * bpp // 8
    untileData = bytearray(real_width * real_height * bpp // 8)
    for y in range(numTileH):            
        for x in range(numTileW):                            
            dataPtr = y * numTileW * tileSize + tileSize * x
            for ty in range(tile_h):
                curHeight = y * tile_h + ty
                curWidth = x * tile_w
                dstIndex = (curHeight * real_width + curWidth) * bpp // 8   
                srcIndex = dataPtr + ty * lineSize
                untileData[dstIndex:dstIndex+lineSize] = pixel[srcIndex:srcIndex+lineSize]    
    cropData = crop(untileData,real_width,real_height,width,height,bpp)
    return cropData
def crop(pixel,real_width,real_height,cropWidth,cropHeight,bpp):
    #Note: this function can't apply to 4bpp
    #for 4bpp: first convert 4bpp to 8bpp then run this function
    #Because some 4bpp array sizes are not integers.
    if real_width == cropWidth and real_height == cropHeight:
        return pixel
    minWidth = min(real_width,cropWidth)
    minHeight = min(real_height,cropHeight)
    length = cropWidth * cropHeight * bpp // 8 
    outPixel = bytearray(length)    
    dstLineSize = minWidth * bpp // 8
    srcLineSize = real_width * bpp // 8

    for y in range(minHeight):        
        dstIndex = y * dstLineSize
        srcIndex = y * srcLineSize
        outPixel[dstIndex:dstIndex+dstLineSize] = pixel[srcIndex:srcIndex+dstLineSize]
    return outPixel
def getRealWH(width,height,tile_w,tile_h):
    real_width = width
    real_height = height
    if (width%tile_w):
        real_width = (width-(width%tile_w))+tile_w            
    if (height%tile_h) :
        real_height = (height-(height%tile_h))+tile_h
    return real_width,real_height
def ia8(rawPixel):
    t = bytearray(4)
    t[0] = rawPixel & 0xFF
    t[1] = rawPixel & 0xFF
    t[2] = rawPixel & 0xFF
    t[3] = rawPixel >> 8
    return t    
def rgb565(rawPixel):
    t = bytearray(4)
    t[0] = (((rawPixel >> 11) & 0x1F) * 0xFF // 0x1F)
    t[1] = (((rawPixel >> 5)  & 0x3F) * 0xFF // 0x3F)
    t[2] = (((rawPixel >> 0)  & 0x1F) * 0xFF // 0x1F)
    t[3] = 0xFF
    return t    
def rgb5a3(rawPixel):
    t = bytearray(4)
    if rawPixel & 0x8000 != 0:  # r5g5b5
        t[0] = (((rawPixel >> 10) & 0x1F) * 0xFF // 0x1F)
        t[1] = (((rawPixel >> 5)  & 0x1F) * 0xFF // 0x1F)
        t[2] = (((rawPixel >> 0)  & 0x1F) * 0xFF // 0x1F)
        t[3] = 0xFF
    else:  # r4g4b4a3
        t[0] = (((rawPixel >> 8)  & 0x0F) * 0xFF // 0x0F)
        t[1] = (((rawPixel >> 4)  & 0x0F) * 0xFF // 0x0F)
        t[2] = (((rawPixel >> 0)  & 0x0F) * 0xFF // 0x0F)
        t[3] = (((rawPixel >> 12) & 0x07) * 0xFF // 0x07)
    return t 
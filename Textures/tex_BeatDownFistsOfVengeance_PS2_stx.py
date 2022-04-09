#ReaderWare Image Textures
#RW Version: 3.6.0.3
#By Allen
from inc_noesis import *
def registerNoesisTypes():
    handle = noesis.register("Beat Down Fists of Vengeance PS2", ".stx")
    noesis.setHandlerTypeCheck(handle, noepyCheckTypeImage)
    noesis.setHandlerLoadRGBA(handle, txdLoadRGBA)
    #noesis.logPopup()
    return 1
def noepyCheckTypeImage(data):
    bs = NoeBitStream(data)
    idstring = bs.readUInt()
    if idstring != 0x18:
            return 0
    return 1
def txdLoadRGBA(data, texList):
    bs = NoeBitStream(data)
    chunk = rwChunk(bs)
    if chunk.chunkID == 0x18:
            datas = bs.readBytes(chunk.chunkSize)
            image = rImage(datas)
            texture = image.read()
            texList.append(texture)
    return 1    
class rwChunk(object):   
        def __init__(self,bs):
                self.chunkID,self.chunkSize,self.chunkVersion = bs.read('3I')   
class rImage(object):     
    def __init__(self,datas):
        self.bs = NoeBitStream(datas)
    def read(self):
        imageStruct = rwChunk(self.bs)
        width = self.bs.readUInt()
        height = self.bs.readUInt()
        depth = self.bs.readUInt() # this game: 8 = 256 colors 8bpp(bits per pixel). 4 = 16 colors 8bpp.
        pitch = self.bs.readUInt() # line size (stride)
        pixelSize = pitch * height
        bpp = depth
        if depth == 4:
            bpp = 8
        real_width = pixelSize * 8 // bpp // height
        pixel = self.bs.readBytes(pixelSize)
        pixel = crop(pixel,real_width,height,width,height,depth)        
        if depth == 8:
            palette = self.bs.readBytes(1024)
            textureData = rapi.imageDecodeRawPal(pixel,palette,width,height,8,"r8g8b8a8")     
        elif depth == 4:
            palette = self.bs.readBytes(64)
            textureData = rapi.imageDecodeRawPal(pixel,palette,width,height,8,"r8g8b8a8")              
        elif depth == 32:
            textureData = pixel
        else:
            print("can't support this format:",depth)
            return 0
        return (NoeTexture("tex", width, height, textureData, noesis.NOESISTEX_RGBA32))                         
       
def crop(pixel,real_width,real_height,cropWidth,cropHeight,bpp):
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
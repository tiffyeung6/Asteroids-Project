"""
Steganography methods for the imager application.

This module provides all of the test processing operations (encode, decode) 
that are called by the application. Note that this class is a subclass of Filter. 
This allows us to layer this functionality on top of the Instagram-filters, 
providing this functionality in one application.

Based on an original file by Dexter Kozen (dck10) and Walker White (wmw2)

Tiffany Yeung (ty272), Luke Shao (lys8)
11/15/2022
"""
import a6filter


class Encoder(a6filter.Filter):
    """
    A class that contains a collection of image processing methods
    
    This class is a subclass of Filter.  That means it inherits all of the 
    methods and attributes of that class too. We do that separate the 
    steganography methods from the image filter methods, making the code
    easier to read.
    
    Both the `encode` and `decode` methods should work with the most recent
    image in the edit history.
    """
    
    def encode(self, text):
        """
        Returns True if it could hide the text; False otherwise.
        
        This method attemps to hide the given message text in the current 
        image. This method first converts the text to a byte list using the 
        encode() method in string to use UTF-8 representation:
            
            blist = list(text.encode('utf-8'))
        
        This allows the encode method to support all text, including emoji.
        
        If the text UTF-8 encoding requires more than 999999 bytes or the 
        picture does  not have enough pixels to store these bytes this method
        returns False without storing the message. However, if the number of
        bytes is both less than 1000000 and less than (# pixels - 10), then 
        the encoding should succeed.  So this method uses no more than 10
        pixels to store additional encoding information.
        
        Parameter text: a message to hide
        Precondition: text is a string
        """
        assert type(text) == str
        current = self.getCurrent()
        start = 'abc'
        x = list(start.encode('utf-8')) 
        blist = list(text.encode('utf-8'))
        end = '%@('
        y = list(end.encode('utf-8'))

        if len(blist) > 999999:
            return False
        if len(x) + len(y) + len(blist) > len(current):
            return False

        newlist = x + blist + y
        
        for i in range(len(newlist)):
            self._encode_pixel(i, newlist[i])
        
        return True

        # You may modify anything in the above specification EXCEPT
        # The first line (Returns True...)
        # The last paragraph (If the text UTF-8 encoding...)
        # The precondition (text is a string)
    
    
    def decode(self):
        """
        Returns the secret message (a string) stored in the current image. 
        
        The message should be decoded as a list of bytes. Assuming that a list
        blist has only bytes (ints in 0.255), you can turn it into a string
        using UTF-8 with the decode method:
            
            text = bytes(blist).decode('utf-8')
        
        If no message is detected, or if there is an error in decoding the
        message, this method returns None
        """
        # You may modify anything in the above specification EXCEPT
        # The first line (Returns the secret...)
        # The last paragraph (If no message is detected...)
        pass    # Implement me
        current = self.getCurrent()
        start = 'abc'
        end = '%@('
        endlist = list(end.encode('utf-8'))

        bytelist = [self._decode_pixel(0), self._decode_pixel(1), self._decode_pixel(2)]
        newstart = bytes(bytelist).decode('utf-8')

        if newstart != start:
            return None
        
        #newlist = []
        position = 3
        while True:
            y = self._decode_pixel(position)
            bytelist.append(y)
            position = position + 1
            
            if position >= len(self.getCurrent()):
                return None
            if bytelist[-3:] == endlist:
                if bytelist == start+end:
                    return ''
                returnlist = bytelist[3:(len(bytelist)-3)]
                new = bytes(returnlist)
                return new.decode('utf-8')
                
            
    # HELPER METHODS
    def _decode_pixel(self, pos):
        """
        Return: the number n hidden in pixel pos of the current image.
        
        This function assumes that the value was a 3-digit number encoded as 
        the last digit in each color channel (e.g. red, green and blue).
        
        Parameter pos: a pixel position
        Precondition: pos is an int with  0 <= p < image length (as a 1d list)
        """
        # This is helper. You do not have to use it. You are allowed to change it.
        # There are no restrictions on how you can change it.
        rgb = self.getCurrent()[pos]
        red   = rgb[0]
        green = rgb[1]
        blue  = rgb[2]
        return  (red % 10) * 100  +  (green % 10) * 10  +  blue % 10
    
    def _encode_pixel(self, pos, b):
        """
        Return: the new 3-digit pixel in the image at position pos given the 
        number n to encode
        
        Parameter n: a number that we want to encode
        Precondition: n is an int with 0 < n < 10
        
        Parameter pos: a pixel position
        Precondition: pos is an int with  0 <= p < image length (as a 1d list)
        """
        current = self.getCurrent()
                        
        assert b<=255 and b>=0
        assert pos < len(current) and 0<=pos
        rgb = current[pos]
        
        #digits of number we want to encode
        first = b//100 
        second = int(b//10) % 10 
        last = b % 10

        red = rgb[0] - (rgb[0] % 10) + first
        green = rgb[1] - (rgb[1] % 10) + second
        blue = rgb[2] - (rgb[2] % 10) + last
        
        if red > 255:
            red = red -10
        if green > 255: 
            green = green -10
        if blue > 255: 
            blue = blue -10

        rgb = (red, green, blue)
        current[pos] = rgb
        return current[pos]
    
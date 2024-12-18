## Angry Generator

A REST API that returns an image or video with the caption provided in the URL.

![Example](example.gif)

This GIF demonstrates how the site can be used to directly embed the generated image as a GIF in Discord.   
By embedding the GIF in Discord, you can easily view and favorite it 
**[To add a GIF to favorites add `.gif` at the end of the caption (This gets cut from the text on the image)].**

A live version is available at [https://angry.realdegrees.dev/](https://angry.realdegrees.dev/adjust%20the%20caption%20in%20the%20url)

### Endpoints

#### GET `/<caption>`
##### Params (Optional)
- `type`: The type of image to be displayed (Currently only supports 'angry') (e.g., `type=mad`)
- `font`: The font to be used for the caption (Currently only supports 'arial') (e.g., `font=arial`)
- `font_size`: The size of the font to be used for the caption (e.g., `font_size=150`)
- `audio`: The audio to be used as a background track (e.g., `audio=chill`)

URL Syntax: `http(s)://<domain>.<tld>/<caption>?type=<type>&font=<font>&font_size=<font_size>`
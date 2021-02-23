import io
import textwrap

import PIL
from PIL import Image, ImageDraw, ImageFont
from discord import Member, Emoji

from cogs.utilities.formatting import format_points


class InventoryImage:
    """A class for generating an image for a user's inventory.

        Properties that aren't provided will be omitted during the render.
        """

    _leaderboard_position: int = 0
    _member: Member = None
    _points_emoji: Emoji = None
    _points_name: str = "points"
    _points_total: float = 0

    _image: Image = None

    def __init__(self, member=None, points_total=0, points_emoji=None, points_name=None, leaderboard_position=None):
        self._member = member
        self._leaderboard_position = leaderboard_position
        self._points_total = points_total
        self._points_emoji = points_emoji
        self._points_name = points_name

    @property
    def image(self):
        return self._image

    def _put_text_with_drop_shadow(self, draw: ImageDraw, coordinates, text: str, **kwargs):
        x = coordinates[0]
        y = coordinates[1]
        font = kwargs.get("font", ImageFont.truetype("/app/assets/fonts/Roboto-Medium.ttf", 36))
        shadow_colour = kwargs.get("shadow_colour", (255, 255, 255, 255))

        draw.multiline_text((x - 1, y - 1), text, font=font, fill=shadow_colour)
        draw.multiline_text((x + 1, y - 1), text, font=font, fill=shadow_colour)
        draw.multiline_text((x - 1, y + 1), text, font=font, fill=shadow_colour)
        draw.multiline_text((x + 1, y + 1), text, font=font, fill=shadow_colour)

        draw.multiline_text(coordinates, text, font=font, fill=kwargs.get("fill"))

    def _wrap_text(self, width, text):
        wrapper = textwrap.TextWrapper(width=width)

        return wrapper.fill(text=text)

    async def generate(self) -> Image:
        font = ImageFont.truetype("/app/assets/fonts/Roboto-Medium.ttf", 36)
        username_font = ImageFont.truetype("/app/assets/fonts/Roboto-Medium.ttf", 48)

        profile_image = self._member.avatar_url_as(format='png')
        profile_image_bytes = io.BytesIO(initial_bytes=await profile_image.read())
        profile_image = Image.open(profile_image_bytes).convert("RGBA").resize((150, 150))

        # get an image
        base = Image.open("/app/assets/inventory-backdrop.png").convert("RGBA").resize((640, 360))

        # get a drawing context
        d = ImageDraw.Draw(base)

        # crop image
        width, height = profile_image.size
        x = (width - height) // 2
        img_cropped = profile_image.crop((x, 0, x + height, height))

        # create grayscale image with white circle (255) on black background (0)
        mask = Image.new('L', img_cropped.size)
        mask_draw = ImageDraw.Draw(mask)
        width, height = img_cropped.size
        mask_draw.ellipse((0, 0, width, height), fill=255)

        # add mask as alpha channel
        img_cropped.putalpha(mask)

        # Put a border around the user's icon in their user colour.
        d.ellipse((25, 25, 35 + width, 35 + height), fill=self._member.colour.to_rgb(), outline=32)

        self._put_text_with_drop_shadow(d, (200, 30),
                                        "{.display_name}#{.discriminator}".format(self._member, self._member),
                                        font=username_font,
                                        fill=self._member.colour.to_rgb())

        self._put_text_with_drop_shadow(d, (275, 100),
                                        "{} {}".format(format_points(self._points_total), self._points_name), font=font,
                                        fill=(255, 255, 255, 255),
                                        shadow_colour=(1, 1, 1, 1))

        self._put_text_with_drop_shadow(d, (40, 250),
                                        self._wrap_text(
                                            40,
                                            "#{} in {.name}".format(self._leaderboard_position, self._member.guild)
                                        ),
                                        font=font,
                                        fill=(255, 255, 255, 255),
                                        shadow_colour=(1, 1, 1, 1))

        base.paste(img_cropped, (30, 30), img_cropped)

        # Load the points emoji from the config, add that to the image.
        emoji_image = self._points_emoji.url_as(format='png')
        emoji_image_bytes = io.BytesIO(initial_bytes=await emoji_image.read())
        emoji_image = Image.open(emoji_image_bytes).convert("RGBA")

        new_width = 50
        new_height = new_width * emoji_image.height / emoji_image.width

        emoji_image.thumbnail((new_width, new_height))

        base.paste(emoji_image, (200, 100), emoji_image)

        return base

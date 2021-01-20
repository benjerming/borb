import io
import logging
import typing
from typing import Optional, Any, Union

from PIL import Image  # type: ignore [import]

from ptext.io.read_transform.image.read_jpeg_image_transformer import image_hash_method
from ptext.io.read_transform.read_base_transformer import (
    ReadBaseTransformer,
    ReadTransformerContext,
)
from ptext.io.read_transform.types import add_base_methods, Stream, AnyPDFType
from ptext.pdf.canvas.event.event_listener import EventListener

logger = logging.getLogger(__name__)


class ReadCCITTFaxImageTransformer(ReadBaseTransformer):
    def can_be_transformed(
        self, object: Union[io.BufferedIOBase, io.RawIOBase, AnyPDFType]
    ) -> bool:
        return (
            isinstance(object, Stream)
            and object.get("Type", None) in ["XObject", None]
            and object.get("Subtype", None) == ("Image")
            and "Filter" in object
            and (
                object["Filter"] == "CCITTFaxDecode"
                or (
                    isinstance(object["Filter"], list)
                    and object["Filter"][0] == "CCITTFaxDecode"
                )
            )
        )

    def transform(
        self,
        object_to_transform: Union[io.BufferedIOBase, io.RawIOBase, AnyPDFType],
        parent_object: Any,
        context: Optional[ReadTransformerContext] = None,
        event_listeners: typing.List[EventListener] = [],
    ) -> Any:

        # use PIL to read image bytes
        assert isinstance(object_to_transform, Stream)
        try:
            tmp = Image.open(io.BytesIO(object_to_transform["Bytes"]))
            tmp.getpixel(
                (0, 0)
            )  # attempting to read pixel 0,0 will trigger an error if the underlying image does not exist
        except:
            logger.debug(
                "Unable to read ccitt fax image. Constructing empty image of same dimensions."
            )
            w = int(object_to_transform["Width"])
            h = int(object_to_transform["Height"])
            tmp = Image.new("RGB", (w, h), (128, 128, 128))

        # add base methods
        add_base_methods(tmp.__class__)

        # add hash method
        setattr(tmp.__class__, "__hash__", image_hash_method)

        # set parent
        tmp.set_parent(parent_object)

        # add event listeners
        for l in event_listeners:
            tmp.add_event_listener(l)

        # return
        return tmp

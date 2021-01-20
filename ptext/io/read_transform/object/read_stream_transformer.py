import io
import typing
from typing import Optional, Any, Union

from ptext.io.filter.stream_decode_util import decode_stream
from ptext.io.read_transform.read_base_transformer import (
    ReadBaseTransformer,
    ReadTransformerContext,
)
from ptext.io.read_transform.types import (
    Stream,
    Reference,
    AnyPDFType,
)
from ptext.pdf.canvas.event.event_listener import EventListener


class ReadStreamTransformer(ReadBaseTransformer):
    def can_be_transformed(
        self, object: Union[io.BufferedIOBase, io.RawIOBase, AnyPDFType]
    ) -> bool:
        return isinstance(object, Stream)

    def transform(
        self,
        object_to_transform: Union[io.BufferedIOBase, io.RawIOBase, AnyPDFType],
        parent_object: Any,
        context: Optional[ReadTransformerContext] = None,
        event_listeners: typing.List[EventListener] = [],
    ) -> Any:

        assert isinstance(object_to_transform, Stream)
        object_to_transform.set_parent(parent_object)  # type: ignore [attr-defined]

        # add listener(s)
        for l in event_listeners:
            object_to_transform.add_event_listener(l)  # type: ignore [attr-defined]

        # resolve references in stream dictionary
        assert context is not None
        assert context.tokenizer is not None
        xref = parent_object.get_root().get("XRef")
        for k, v in object_to_transform.items():
            if isinstance(v, Reference):
                v = xref.get_object(v, context.tokenizer.io_source, context.tokenizer)
                object_to_transform[k] = v

        # apply filter(s)
        object_to_transform = decode_stream(object_to_transform)

        # convert (remainder of) stream dictionary
        for k, v in object_to_transform.items():
            if not isinstance(v, Reference):
                v = self.get_root_transformer().transform(
                    v, object_to_transform, context, []
                )
                if v is not None:
                    object_to_transform[k] = v

        # linkage
        object_to_transform.set_parent(parent_object)  # type: ignore [attr-defined]

        # return
        return object_to_transform

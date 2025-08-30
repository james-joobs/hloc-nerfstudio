#!/bin/bash
# ns-viewer wrapper with viser compatibility patch

# Apply the patch before running ns-viewer
python -c "
import sys
try:
    # Monkey-patch viser message registry
    import viser.infra._messages as messages
    
    # Create a fake CameraMessage class that matches what nerfstudio expects
    from dataclasses import dataclass
    from typing import Tuple, Optional
    
    @dataclass
    class CameraMessage:
        '''Camera message for nerfstudio compatibility'''
        aspect: float
        render_height: int
        render_width: int
        fov: float
        matrix: Tuple[float, ...]
        camera_type: str = 'perspective'
        is_moving: bool = False
        timestamp: Optional[float] = None
        
        @classmethod
        def deserialize(cls, data):
            '''Deserialize from dict'''
            return cls(**data)
    
    # Register it in the message type registry
    if hasattr(messages.Message, '_subclass_from_type_string'):
        registry = messages.Message._subclass_from_type_string()
        registry['CameraMessage'] = CameraMessage
        
        # Also add it to the messages module
        messages.CameraMessage = CameraMessage
        
    print('✅ viser CameraMessage compatibility patch applied')
except Exception as e:
    print(f'⚠️ Could not apply patch: {e}')
    sys.exit(1)
" || exit 1

# Now run the actual ns-viewer command
exec ns-viewer "$@"
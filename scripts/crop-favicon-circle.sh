#!/bin/bash
set -e

# Crop favicon.svg and favicon.ico into circles
# Requires ImageMagick (convert/magick command)

PUBLIC_DIR="public"
SIZE=512

echo "Creating circular favicons..."

# SVG to circular PNG, then back to SVG with clip path
if [ -f "$PUBLIC_DIR/favicon.svg" ]; then
  echo "Processing favicon.svg..."

  # Convert SVG to large PNG
  convert -background none "$PUBLIC_DIR/favicon.svg" -resize ${SIZE}x${SIZE} /tmp/favicon_temp.png

  # Create circular crop (using implicit alpha composite)
  convert /tmp/favicon_temp.png \
    -bordercolor none -border 0 \
    \( +clone -alpha extract -draw 'fill black polygon 0,0 0,'$SIZE' '$SIZE','$SIZE' '$SIZE',0' \
       -alpha off -write mpr:mask +delete \) \
    -mask mpr:mask -write /tmp/favicon_circle.png +delete

  # Convert back to SVG format (embed as base64 or use as reference)
  # For practical favicon use, we'll keep the SVG and add a note about the circular version
  cp /tmp/favicon_circle.png "$PUBLIC_DIR/favicon-circle.png"
  echo "  ✓ Created favicon-circle.png"
fi

# ICO to circular
if [ -f "$PUBLIC_DIR/favicon.ico" ]; then
  echo "Processing favicon.ico..."

  # Convert ICO to PNG
  convert "$PUBLIC_DIR/favicon.ico" -resize ${SIZE}x${SIZE} /tmp/favicon_ico_temp.png

  # Create circular crop
  convert /tmp/favicon_ico_temp.png \
    -bordercolor none -border 0 \
    \( +clone -alpha extract -draw 'fill black polygon 0,0 0,'$SIZE' '$SIZE','$SIZE' '$SIZE',0' \
       -alpha off -write mpr:mask +delete \) \
    -mask mpr:mask \
    -background none -gravity center -extent ${SIZE}x${SIZE} \
    /tmp/favicon_circle_ico.png

  # Convert back to ICO
  convert /tmp/favicon_circle_ico.png "$PUBLIC_DIR/favicon-circle.ico"
  echo "  ✓ Created favicon-circle.ico"
fi

# Cleanup
rm -f /tmp/favicon_temp.png /tmp/favicon_ico_temp.png /tmp/favicon_circle_ico.png

echo "Done! Generated:"
echo "  - public/favicon-circle.png"
echo "  - public/favicon-circle.ico"

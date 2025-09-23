# Spanish Images Creation Guide

## Overview
The app now supports bilingual images! When users switch to Spanish, the app will automatically load Spanish versions of images from the `images/es/` folder.

## Current Status
✅ **System is ready** - The app will automatically switch between English and Spanish images
✅ **Folder structure created** - `images/en/` and `images/es/` folders exist
✅ **Placeholder images copied** - English images copied to Spanish folder as placeholders

## Images That Need Spanish Text

### Destination Images (Destinos)
1. **`highlands.png`** → Should show "Las Tierras Altas" or "Highlands"
2. **`town.png`** → Should show "Puerto Ayora" (same text, but maybe different styling)
3. **`airport.png`** → Should show "Aeropuerto"
4. **`other.png`** → Should show "Otro"

### People Images (Personas)
5. **`student.png`** → Should show "Estudiantes"
6. **`tourist.png`** → Should show "Turista Individual"
7. **`2tourists.png`** → Should show "Múltiples Turistas"
8. **`local.png`** → Should show "Locales"
9. **`otherpeople.png`** → Should show "Pasajeros Varios"

### Cargo Images (Carga)
10. **`luggage.png`** → Should show "Equipaje"
11. **`farm.png`** → Should show "Equipo de Trabajo"
12. **`food.png`** → Should show "Comida y Productos"

## How to Create Spanish Images

### Option 1: Image Editing Software
1. Open each image in an image editor (Photoshop, GIMP, Canva, etc.)
2. Replace the English text with the Spanish equivalent
3. Keep the same image dimensions and style
4. Save as PNG with the same filename in `images/es/` folder

### Option 2: Online Tools
- Use Canva, Figma, or similar online design tools
- Import the original image
- Edit the text overlay
- Export as PNG

### Option 3: AI Image Generation
- Use AI tools like DALL-E, Midjourney, or Stable Diffusion
- Generate new images with Spanish text
- Ensure they match the style and purpose of the originals

## Spanish Text Translations

| English | Spanish |
|---------|---------|
| The Highlands | Las Tierras Altas |
| Puerto Ayora | Puerto Ayora |
| Airport | Aeropuerto |
| Other | Otro |
| Students | Estudiantes |
| Single Tourist | Turista Individual |
| Multiple Tourists | Múltiples Turistas |
| Locals | Locales |
| Miscellaneous Passengers | Pasajeros Varios |
| Luggage | Equipaje |
| Work Equipment | Equipo de Trabajo |
| Food and Goods | Comida y Productos |
| Miscellaneous Cargo | Carga Variada |

## Testing the System

1. Run the app: `py main.py`
2. Click the language toggle button (ES/EN) in the top-right corner
3. Navigate to the Destination, People, or Cargo screens
4. Verify that images change when switching languages

## File Locations

```
Galapagos-2025/
├── images/
│   ├── en/          # English images
│   │   ├── highlands.png
│   │   ├── town.png
│   │   ├── airport.png
│   │   ├── other.png
│   │   ├── student.png
│   │   ├── tourist.png
│   │   ├── 2tourists.png
│   │   ├── local.png
│   │   ├── otherpeople.png
│   │   ├── luggage.png
│   │   ├── farm.png
│   │   └── food.png
│   └── es/          # Spanish images (replace these!)
│       ├── highlands.png
│       ├── town.png
│       ├── airport.png
│       ├── other.png
│       ├── student.png
│       ├── tourist.png
│       ├── 2tourists.png
│       ├── local.png
│       ├── otherpeople.png
│       ├── luggage.png
│       ├── farm.png
│       └── food.png
```

## Notes
- The system automatically falls back to the root directory images if Spanish versions don't exist
- Keep the same file names and PNG format
- Maintain similar visual style and dimensions
- Test thoroughly after replacing images

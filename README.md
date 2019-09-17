# VNOnDB Online to Offline dataset converter

# Run
## Help
- `python --help` for help

## Quick run!
`python InkData_line line`
`python InkData_word word`
`python InkData_paragraph paragraph`

## Detail
- `python <data_path> <output_dir> --line_width <line_width> --dpi <dpi>`
  - `<data_path>` is a directory contains `*.inkml` files of dataset, will be one of `InkData_word`, `InkData_line` or `InkData_paragraph` if download and extract from the main page
  - `<output_dir>` is where image and label files converted will be placed. Directory will be created if not existed.
  - (Optional) `<line_width>` is line stroke width, default is `2`
  - (Optional) `<dpi>`, default is `300`
# Monitor EDID Information

This directory contains Extended Display Identification Data (EDID) information extracted from your connected monitors, with a focus on your 4K monitor connected via HDMI-0.

## What is EDID?

EDID (Extended Display Identification Data) is a data structure provided by a digital display to describe its capabilities to a video source (e.g., graphics card). It includes information such as:

- Manufacturer name and serial number
- Product type
- Physical dimensions
- Supported display resolutions and refresh rates
- Color characteristics
- Timing information

## Files in this Directory

- **summary.txt**: Overview of all connected monitors and a summary of the extracted information
- **edid_raw.txt**: Raw EDID data extracted using get-edid and parse-edid
- **edid_raw_output.txt**: Direct output from the get-edid command
- **edid_parsed.txt**: Parsed EDID data in a more readable format
- **all_monitors_edid.txt**: EDID information for all connected monitors
- **hdmi0_edid.txt**: EDID information specifically for the 4K monitor connected via HDMI-0
- **edid.bin**: Binary EDID data extracted from the monitor
- **edid_decoded.txt**: Decoded EDID information using edid-decode

## Monitor Information

Based on the extracted data, your 4K monitor (HDMI-0) has the following specifications:

- **Model**: K3-3
- **Manufacturer**: DZX
- **Physical Size**: 600mm x 330mm
- **Maximum Resolution**: 3840x2160 (4K UHD)
- **Refresh Rate**: 60Hz
- **Connector Type**: HDMI
- **Manufactured**: Week 22 of 2022

## How to Update This Information

If you connect a different monitor or want to refresh this information, run the `extract_edid.sh` script located in the original extraction directory:

```bash
cd ~/Desktop/Projects/Personal/EEID\ extraction\ 4k\ monitor/
./extract_edid.sh
```

This will update all the files in this directory with the latest EDID information from your connected monitors.

## Additional Resources

- [EDID on Wikipedia](https://en.wikipedia.org/wiki/Extended_Display_Identification_Data)
- [EDID Standard Documentation](https://vesa.org/vesa-standards/) 
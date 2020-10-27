def rx_mix(rx_tuple, value):
    """Build up the regular expression string for the XML

    When the value has a % in the lead, we need to build
      a tuple and prepare the string for use in building
      an XML template for NetLogo invocation.

    Otherwise, we are reading the .nlogo file in and just
      adding capture groups to populate the Behavior
      Space metadata for the model.
    """
    if value[:1] == "%":
        return rx_tuple[0].replace("__VALUE__", "%s") % tuple(
            [value.replace("__KEY__", x) for x in rx_tuple[1]]
        )
    else:
        return rx_tuple[0].replace("__VALUE__", value)


rxe = (rx_mix(RX0, EXTRACT), rx_mix(RX1, EXTRACT), rx_mix(RX2, EXTRACT))
rxi = (rx_mix(RX0, INSERT), rx_mix(RX1, INSERT), rx_mix(RX2, INSERT))

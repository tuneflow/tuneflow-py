from typing_extensions import TypedDict, Required, NotRequired


class AudioPluginDescriptor(TypedDict):
    '''
    Descriptor of an audio plugin.
    '''

    category: NotRequired[str]
    '''
    Category of the plugin.
    e.g.: 'Instrument|Synth', 'Fx|EQ', etc.
    '''

    descriptiveName: NotRequired[str]
    ''' A more detailed name. '''

    id: Required[str]
    ''' An internal id of the plugin. '''

    isInstrument: Required[str]
    '''
    Whether this plugin can be used as an instrument to generate
    sound from MIDI notes.
    '''

    manufacturerName: Required[str]
    ''' Manufacturer of the plugin. '''

    name: Required[str]
    '''
    A short name of the plugin.
    Use this when creating `AudioPlugin` instances.
    '''

    pluginFormatName: Required[str]
    ''' Format of the plugin. e.g. 'VST3', 'AudioUnit', etc. '''

    version: Required[str]
    ''' Version of the plugin. '''

from typing_extensions import TypedDict


class AudioPluginDescriptor(TypedDict, total=False):
    '''
    Descriptor of an audio plugin.
    '''

    category: str
    '''
    Category of the plugin.
    e.g.: 'Instrument|Synth', 'Fx|EQ', etc.
    '''

    descriptiveName: str
    ''' A more detailed name. '''

    id: str
    ''' An internal id of the plugin. '''

    isInstrument: str
    '''
    Whether this plugin can be used as an instrument to generate
    sound from MIDI notes.
    '''

    manufacturerName: str
    ''' Manufacturer of the plugin. '''

    name: str
    '''
    A short name of the plugin.
    Use this when creating `AudioPlugin` instances.
    '''

    pluginFormatName: str
    ''' Format of the plugin. e.g. 'VST3', 'AudioUnit', etc. '''

    version: str
    ''' Version of the plugin. '''

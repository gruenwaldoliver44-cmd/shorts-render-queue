import {registerRoot, Composition} from 'remotion';
import {Probe, PROBE_LEN} from './Probe.jsx';
const Root = () => (<>
  <Composition id="Probe" component={Probe} durationInFrames={PROBE_LEN} fps={30} width={1920} height={1080}/>
</>);
registerRoot(Root);

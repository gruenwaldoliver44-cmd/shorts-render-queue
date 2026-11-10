import {registerRoot,Composition} from 'remotion';import {Main} from './Main';import t from './timeline.json';
registerRoot(()=><Composition id="P" component={Main} durationInFrames={t.dur} width={1920} height={1080} fps={30}/>);

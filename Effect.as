package {
	import flash.media.Sound;

	public class Effect {
		var action:Function;
		var sound:Sound;

		public function Effect(action:Function, sound:Sound) {
			this.action = action;
			this.sound = sound;
		}

		public function affect():void {
			sound.play();
			action();
		}
	}
}

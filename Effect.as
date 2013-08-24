package {

	public class Effect {
		var warnFunction:Function;
		var effectFunction:Function;

		public function Effect(warnFunction:Function, effectFunction:Function) {
			this.warnFunction = warnFunction;
			this.effectFunction = effectFunction;
		}

		public function warn():void {
			warnFunction();
		}

		public function affect():void {
			effectFunction();
		}
	}
}

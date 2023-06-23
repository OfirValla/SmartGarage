import { TailSpin } from 'react-loader-spinner';

const Loader = () => (
    <TailSpin
        height="80"
        width="80"
        color="#fefefe"
        ariaLabel="tail-spin-loading"
        radius="1"
        wrapperStyle={{}}
        wrapperClass=""
        visible={true}
    />
);

export default Loader;
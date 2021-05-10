#ifndef __OUTPUT_HXX_
#define __OUTPUT_HXX_

template <class T>
void fillParticle(Particle& particle, PartList& fillArray, T& fillObject, std::vector<Int_t>& bitMap)
{
    for (size_t syst = 0; syst < fillArray.size(); ++syst) {
        for (auto idx : fillArray[syst]) {
            bitMap[idx] += 1 << syst;
        }
    }
    for (size_t idx = 0; idx < particle.pt->GetSize(); ++idx) {
        if (bitMap.at(idx) != 0) {
            fillObject.pt.push_back(particle.pt->At(idx));
            fillObject.eta.push_back(particle.eta->At(idx));
            fillObject.phi.push_back(particle.phi->At(idx));
            fillObject.mass.push_back(particle.mass->At(idx));
        }
    }
    fillObject.syst_bitMap = bitMap;
    fillObject.syst_bitMap.erase(remove(fillObject.syst_bitMap.begin(),
                                     fillObject.syst_bitMap.end(), 0),
        fillObject.syst_bitMap.end());
}

template <class T>
void fillParticle(Particle& particle, PartList& fillArray, T& fillObject)
{
    std::vector<Int_t> bitMap(particle.pt->GetSize());
    fillParticle(particle, fillArray, fillObject, bitMap);
}

#endif // __OUTPUT_HXX_

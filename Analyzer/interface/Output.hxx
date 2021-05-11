#ifndef __OUTPUT_HXX_
#define __OUTPUT_HXX_

template <class T>
void fillParticle(Particle& particle, int listName, T& fillObject, std::vector<Int_t>& bitMap, std::vector<bool> passVec)
{
    for (size_t syst = 0; syst < Particle::nSyst; ++syst) {
        if (!passVec.at(syst)) {
            continue;
        }
        for (auto idx : particle.list(listName, syst)) {
            bitMap[idx] += 1 << syst;
        }
    }
    for (size_t idx = 0; idx < particle.size(); ++idx) {
        if (bitMap.at(idx) != 0) {
            fillObject.pt.push_back(particle.pt(idx));
            fillObject.eta.push_back(particle.eta(idx));
            fillObject.phi.push_back(particle.phi(idx));
            fillObject.mass.push_back(particle.mass(idx));
        }
    }
    fillObject.syst_bitMap = bitMap;
    fillObject.syst_bitMap.erase(remove(fillObject.syst_bitMap.begin(),
                                     fillObject.syst_bitMap.end(), 0),
        fillObject.syst_bitMap.end());
}

template <class T>
void fillParticle(Particle& particle, int listName, T& fillObject, std::vector<bool> passVec)
{
    std::vector<Int_t> bitMap(particle.size());
    fillParticle(particle, listName, fillObject, bitMap, passVec);
}

#endif // __OUTPUT_HXX_
